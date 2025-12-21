<template>
  <div class="pdf-annotator">
    <div class="annotator-toolbar" v-if="!readonly">
      <el-button-group>
        <el-button 
          :type="tool === 'move' ? 'primary' : 'default'"
          @click="setTool('move')"
          size="small"
          title="移动PDF"
        >
          <el-icon><Rank /></el-icon>
          移动
        </el-button>
        <el-button 
          :type="tool === 'pen-red' ? 'primary' : 'default'"
          @click="setTool('pen-red')"
          size="small"
        >
          <el-icon><EditPen /></el-icon>
          红笔
        </el-button>
        <el-button 
          :type="tool === 'pen-blue' ? 'primary' : 'default'"
          @click="setTool('pen-blue')"
          size="small"
        >
          <el-icon><EditPen /></el-icon>
          蓝笔
        </el-button>
        <el-button 
          :type="tool === 'text' ? 'primary' : 'default'"
          @click="setTool('text')"
          size="small"
          title="添加/编辑文本"
        >
          <el-icon><Document /></el-icon>
          文本
        </el-button>
        <el-button 
          :type="tool === 'select-text' ? 'primary' : 'default'"
          @click="setTool('select-text')"
          size="small"
          title="选择并移动文本"
        >
          <el-icon><Pointer /></el-icon>
          选择文本
        </el-button>
        <el-button 
          @click="undo"
          size="small"
          :disabled="history.length === 0"
        >
          <el-icon><RefreshLeft /></el-icon>
          撤销
        </el-button>
        <el-button 
          @click="clear"
          size="small"
          :disabled="elements.length === 0"
        >
          <el-icon><Delete /></el-icon>
          清空
        </el-button>
        <el-button 
          @click="rotatePDF"
          size="small"
          title="旋转90度"
        >
          <el-icon><RefreshRight /></el-icon>
          旋转
        </el-button>
      </el-button-group>
      <div class="page-controls">
        <el-button 
          @click="prevPage"
          size="small"
          :disabled="currentPage <= 1"
        >
          <el-icon><ArrowLeft /></el-icon>
          上一页
        </el-button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <el-button 
          @click="nextPage"
          size="small"
          :disabled="currentPage >= totalPages"
        >
          下一页
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
    </div>
    
    <div class="annotator-content" v-if="pdfUrl" ref="contentRef" @wheel.prevent="onWheel">
      <div 
        class="pdf-wrapper" 
        ref="pdfWrapperRef"
        :style="{
          transform: `translate(${translateX}px, ${translateY}px) scale(${scale}) rotate(${rotateAngle}deg)`,
          transformOrigin: 'center center'
        }"
      >
        <canvas 
          ref="pdfCanvasRef"
          class="pdf-canvas"
        ></canvas>
        <canvas 
          ref="canvasRef"
          class="annotation-canvas"
          :class="{ 'readonly-canvas': readonly, 'move-cursor': tool === 'move' }"
          @mousedown="!readonly && onMouseDown($event)"
          @mousemove="!readonly && onMouseMove($event)"
          @mouseup="!readonly && onMouseUp($event)"
          @mouseleave="!readonly && onMouseUp($event)"
        ></canvas>
      </div>
    </div>
    <el-empty v-else description="暂无PDF" :image-size="100" />
    
    <!-- 文本输入对话框 -->
    <el-dialog 
      v-model="showTextDialog" 
      title="添加文本批注" 
      width="500px"
      @closed="cancelTextInput"
    >
      <el-form label-width="100px">
        <el-form-item label="文本内容">
          <el-input
            v-model="textInput"
            type="textarea"
            :rows="3"
            placeholder="请输入批注文本"
            @keyup.enter.ctrl="confirmTextInput"
            ref="textInputRef"
          />
        </el-form-item>
        <el-form-item label="文本颜色">
          <el-color-picker v-model="textColor" />
          <span style="margin-left: 10px;">{{ textColor }}</span>
        </el-form-item>
        <el-form-item label="框体颜色">
          <el-color-picker v-model="boxColor" />
          <span style="margin-left: 10px;">{{ boxColor }}</span>
        </el-form-item>
        <el-form-item label="框体透明度">
          <el-slider 
            v-model="boxOpacity" 
            :min="0" 
            :max="100" 
            :step="10"
            show-input
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cancelTextInput">取消</el-button>
        <el-button type="primary" @click="confirmTextInput">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onBeforeUnmount, markRaw, shallowRef, computed } from 'vue';
import { EditPen, Document, RefreshLeft, Delete, Rank, Pointer, ArrowLeft, ArrowRight, RefreshRight } from '@element-plus/icons-vue';
import { getImageUrl } from '@/utils/image';
import * as pdfjsLib from 'pdfjs-dist';

// 设置PDF.js worker - 使用固定版本号，避免动态版本可能的问题
// 使用unpkg CDN，版本号与package.json中的pdfjs-dist版本保持一致
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://unpkg.com/pdfjs-dist@5.4.449/build/pdf.worker.min.mjs';

const props = defineProps({
  pdfUrl: {
    type: String,
    default: '',
  },
  modelValue: {
    type: Object,
    default: () => ({ version: 1, elements: [] }),
  },
  readonly: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['update:modelValue']);

const pdfCanvasRef = ref(null);
const canvasRef = ref(null);
const pdfWrapperRef = ref(null);
const contentRef = ref(null);
const textInputRef = ref(null);
const showTextDialog = ref(false);
const textInput = ref('');
const textPosition = ref({ x: 0, y: 0 });
const textColor = ref('#000000');
const boxColor = ref('#ffffff');
const boxOpacity = ref(80);

const tool = ref('move');
const isDrawing = ref(false);
const currentPath = ref([]);

const scale = ref(1);
const translateX = ref(0);
const translateY = ref(0);
const rotateAngle = ref(0); // 旋转角度（度）
const isDragging = ref(false);
const dragStart = ref({ x: 0, y: 0 });
const dragStartTranslate = ref({ x: 0, y: 0 });
// 按页面存储批注：{ pageNum: [elements] }
const elementsByPage = ref({});
const history = ref([]);

// 当前页面的批注（计算属性）
const elements = computed({
  get: () => {
    const page = currentPage.value;
    if (!elementsByPage.value[page]) {
      elementsByPage.value[page] = [];
    }
    return elementsByPage.value[page];
  },
  set: (newElements) => {
    const page = currentPage.value;
    elementsByPage.value[page] = newElements || [];
    // 确保响应式更新
    elementsByPage.value = { ...elementsByPage.value };
  }
});

const selectedTextIndex = ref(-1);
const isDraggingText = ref(false);
const isResizingText = ref(false);
const textDragStart = ref({ x: 0, y: 0 });
const textResizeHandle = ref('');
const textResizeStart = ref({ x: 0, y: 0, width: 0, height: 0 });

// PDF相关
// 使用 shallowRef 防止 Vue 代理 PDF 文档对象，避免无法访问私有成员的问题
const pdfDoc = shallowRef(null);
const currentPage = ref(1);
const totalPages = ref(0);
const pageScale = ref(1.5); // PDF渲染缩放比例

// 监听 modelValue 变化
let isUpdatingFromProps = false;
let isUndoing = false;
watch(() => props.modelValue, (newValue) => {
  if (isUpdatingFromProps || isUndoing) return;
  if (newValue) {
    // 支持两种格式：
    // 1. 旧格式：{ version: 1, elements: [] } - 所有页面共用
    // 2. 新格式：{ version: 2, pages: { 1: [], 2: [] } } - 按页面存储
    if (newValue.version === 2 && newValue.pages) {
      // 新格式：按页面存储
      const newPages = JSON.parse(JSON.stringify(newValue.pages));
      if (JSON.stringify(elementsByPage.value) !== JSON.stringify(newPages)) {
        elementsByPage.value = newPages;
        history.value = [];
        nextTick(() => {
          redraw();
        });
      }
    } else if (newValue.elements) {
      // 旧格式：所有页面共用，转换为新格式
      const newElements = JSON.parse(JSON.stringify(newValue.elements));
      // 将旧格式转换为新格式，所有页面使用相同的批注
      const convertedPages = {};
      for (let page = 1; page <= totalPages.value; page++) {
        convertedPages[page] = JSON.parse(JSON.stringify(newElements));
      }
      if (JSON.stringify(elementsByPage.value) !== JSON.stringify(convertedPages)) {
        elementsByPage.value = convertedPages;
        history.value = [];
        nextTick(() => {
          redraw();
        });
      }
    }
  }
}, { deep: true, immediate: true });

// 监听 elementsByPage 变化
watch(elementsByPage, (newPages) => {
  if (isUpdatingFromProps || isUndoing) return;
  isUpdatingFromProps = true;
  const newValue = {
    version: 2,
    pages: JSON.parse(JSON.stringify(newPages)),
  };
  const currentValue = props.modelValue;
  if (!currentValue || JSON.stringify(currentValue) !== JSON.stringify(newValue)) {
    emit('update:modelValue', newValue);
  }
  nextTick(() => {
    isUpdatingFromProps = false;
  });
}, { deep: true, flush: 'post' });

// 监听页码变化，重新渲染PDF并切换批注
watch(currentPage, (newPage, oldPage) => {
  // 切换页面前，确保当前页的批注已保存到 elementsByPage
  // 通过访问 elements.value 确保当前页数据已加载
  if (oldPage) {
    // 确保旧页面的数据已保存（通过 computed getter 已经自动初始化）
    // 强制触发响应式更新
    const oldElements = elementsByPage.value[oldPage];
    if (oldElements) {
      elementsByPage.value = { ...elementsByPage.value };
    }
  }
  
  if (pdfDoc.value && !pdfDoc.value.destroyed) {
    renderPDFPage();
  }
  // 切换页面时，清空当前路径和历史记录
  currentPath.value = [];
  isDrawing.value = false;
  selectedTextIndex.value = -1;
  isDraggingText.value = false;
  isResizingText.value = false;
  
  // 确保新页面的批注数组已初始化（computed getter 会自动处理）
  // 但为了确保响应式，我们显式触发一次
  if (!elementsByPage.value[newPage]) {
    elementsByPage.value[newPage] = [];
    elementsByPage.value = { ...elementsByPage.value };
  }
});

const setTool = (newTool) => {
  tool.value = newTool;
  isDrawing.value = false;
  isDragging.value = false;
  isDraggingText.value = false;
  isResizingText.value = false;
  currentPath.value = [];
  if (newTool !== 'select-text') {
    selectedTextIndex.value = -1;
  }
  redraw();
};

const onWheel = (event) => {
  if (props.readonly) return;
  event.preventDefault();
  const delta = event.deltaY > 0 ? -0.1 : 0.1;
  const newScale = Math.max(0.1, Math.min(5, scale.value + delta));
  scale.value = newScale;
  // 缩放后重新居中
  nextTick(() => {
    centerContent();
  });
};

const prevPage = () => {
  if (!pdfDoc.value || pdfDoc.value.destroyed) return;
  if (currentPage.value > 1) {
    currentPage.value--;
    nextTick(() => {
      centerContent();
    });
  }
};

const nextPage = () => {
  if (!pdfDoc.value || pdfDoc.value.destroyed) return;
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
    nextTick(() => {
      centerContent();
    });
  }
};

// 旋转PDF
const rotatePDF = () => {
  rotateAngle.value = (rotateAngle.value + 90) % 360;
  nextTick(() => {
    centerContent();
  });
};

// 居中显示内容
const centerContent = () => {
  if (!contentRef.value || !pdfCanvasRef.value) return;
  
  nextTick(() => {
    const container = contentRef.value;
    const pdfCanvas = pdfCanvasRef.value;
    if (!container || !pdfCanvas) return;
    
    const containerRect = container.getBoundingClientRect();
    const canvasWidth = pdfCanvas.width;
    const canvasHeight = pdfCanvas.height;
    
    // 考虑旋转后的尺寸
    let displayWidth = canvasWidth * scale.value;
    let displayHeight = canvasHeight * scale.value;
    
    // 如果旋转了90度或270度，交换宽高
    if (rotateAngle.value === 90 || rotateAngle.value === 270) {
      [displayWidth, displayHeight] = [displayHeight, displayWidth];
    }
    
    // 计算居中位置
    const centerX = (containerRect.width - displayWidth) / 2;
    const centerY = (containerRect.height - displayHeight) / 2;
    
    translateX.value = centerX;
    translateY.value = centerY;
  });
};

// 清理PDF文档
const cleanupPDF = () => {
  if (pdfDoc.value) {
    try {
      // 检查文档是否已经被销毁
      if (!pdfDoc.value.destroyed) {
        pdfDoc.value.destroy();
      }
    } catch (error) {
      // 忽略销毁错误，可能是文档已经被销毁或无法访问私有成员
      // 这是正常的，因为 Vue 的代理可能无法访问 PDF.js 的私有字段
      console.warn('清理PDF文档时出错（可忽略）:', error);
    }
    pdfDoc.value = null;
  }
  totalPages.value = 0;
  currentPage.value = 1;
  
  // 清空canvas
  if (pdfCanvasRef.value) {
    const ctx = pdfCanvasRef.value.getContext('2d');
    if (ctx) {
      ctx.clearRect(0, 0, pdfCanvasRef.value.width, pdfCanvasRef.value.height);
    }
  }
};

// 加载PDF
const loadPDF = async () => {
  if (!props.pdfUrl) {
    cleanupPDF();
    return;
  }
  
  // 先清理旧的PDF文档
  cleanupPDF();
  
  try {
    const fullUrl = props.pdfUrl.startsWith('http') ? props.pdfUrl : getImageUrl(props.pdfUrl, true);
    
    // 添加请求配置，支持CORS和认证
    const loadingTask = pdfjsLib.getDocument({
      url: fullUrl,
      httpHeaders: {},
      withCredentials: false,
    });
    
    const doc = await loadingTask.promise;
    // 使用 markRaw 防止 Vue 代理 PDF 文档对象
    pdfDoc.value = markRaw(doc);
    
    // 检查PDF文档是否有效
    if (!pdfDoc.value || pdfDoc.value.destroyed) {
      console.error('PDF文档无效或已被销毁');
      cleanupPDF();
      return;
    }
    
    totalPages.value = pdfDoc.value.numPages;
    currentPage.value = 1;
    
    // 重置旋转角度和缩放，确保每次加载新PDF时从初始状态开始
    rotateAngle.value = 0;
    scale.value = 1;
    translateX.value = 0;
    translateY.value = 0;
    
    await renderPDFPage();
  } catch (error) {
    console.error('PDF加载失败:', error);
    cleanupPDF();
  }
};

// 渲染PDF页面
const renderPDFPage = async () => {
  if (!pdfDoc.value || !pdfCanvasRef.value) return;
  
  // 检查PDF文档是否有效
  if (pdfDoc.value.destroyed) {
    console.warn('PDF文档已被销毁，无法渲染');
    return;
  }
  
  try {
    // 检查当前页面是否有效
    if (currentPage.value < 1 || currentPage.value > totalPages.value) {
      console.warn('无效的页面编号:', currentPage.value);
      return;
    }
    
    const page = await pdfDoc.value.getPage(currentPage.value);
    
    // 再次检查PDF文档状态（可能在getPage过程中被销毁）
    if (!pdfDoc.value || pdfDoc.value.destroyed || !pdfCanvasRef.value) {
      console.warn('PDF文档在渲染过程中被销毁');
      return;
    }
    
    // 获取页面的旋转角度（PDF 可能包含旋转信息）
    // PDF 的旋转角度通常是 0, 90, 180, 270
    // 如果页面本身有旋转，我们需要补偿它，使其正常显示
    const pageRotation = page.rotate || 0;
    
    // 获取视口
    // 注意：如果 PDF 页面本身有旋转（比如 180 度），我们需要补偿它
    // 通过设置 rotation: 0 来忽略页面的旋转信息，或者通过计算补偿
    // 这里我们先尝试使用 0 度，如果页面本身有旋转，PDF.js 会自动处理
    const viewport = page.getViewport({ 
      scale: pageScale.value,
      rotation: 0  // 始终使用 0 度，让 PDF.js 按照页面的原始方向渲染
    });
    
    const canvas = pdfCanvasRef.value;
    const context = canvas.getContext('2d');
    
    canvas.height = viewport.height;
    canvas.width = viewport.width;
    canvas.style.height = `${viewport.height}px`;
    canvas.style.width = `${viewport.width}px`;
    
    const renderContext = {
      canvasContext: context,
      viewport: viewport,
    };
    
    await page.render(renderContext).promise;
    
    // 设置批注canvas尺寸
    nextTick(() => {
      if (pdfDoc.value && !pdfDoc.value.destroyed && pdfCanvasRef.value && canvasRef.value) {
        setupCanvas();
        redraw();
        centerContent();
      }
    });
  } catch (error) {
    console.error('PDF页面渲染失败:', error);
    // 如果是文档被销毁的错误，清理状态
    if (error.message && error.message.includes('destroyed')) {
      cleanupPDF();
    }
  }
};

const setupCanvas = () => {
  if (!canvasRef.value || !pdfCanvasRef.value) return;
  
  const canvas = canvasRef.value;
  const pdfCanvas = pdfCanvasRef.value;
  
  // 确保批注canvas和PDF canvas的尺寸完全一致
  canvas.width = pdfCanvas.width;
  canvas.height = pdfCanvas.height;
  canvas.style.width = `${pdfCanvas.width}px`;
  canvas.style.height = `${pdfCanvas.height}px`;
  
  // 确保样式尺寸也一致
  canvas.style.position = 'absolute';
  canvas.style.top = '0';
  canvas.style.left = '0';
};

const getCanvasCoordinates = (event) => {
  if (!canvasRef.value || !pdfWrapperRef.value || !pdfCanvasRef.value) return { x: 0, y: 0 };
  
  const canvas = canvasRef.value;
  const wrapper = pdfWrapperRef.value;
  const pdfCanvas = pdfCanvasRef.value;
  const rect = wrapper.getBoundingClientRect();
  
  // 获取鼠标相对于wrapper的位置
  const mouseX = event.clientX - rect.left;
  const mouseY = event.clientY - rect.top;
  
  // 减去变换（平移），得到相对于wrapper内部的位置
  const relativeX = mouseX - translateX.value;
  const relativeY = mouseY - translateY.value;
  
  // 除以缩放比例，得到相对于未缩放的canvas的位置
  const unscaledX = relativeX / scale.value;
  const unscaledY = relativeY / scale.value;
  
  // canvas和PDF canvas的实际像素尺寸应该一致（在setupCanvas中设置）
  // 由于canvas和PDF canvas尺寸一致，坐标直接对应
  // 但需要考虑PDF canvas的样式尺寸（可能通过CSS缩放）
  const pdfCanvasWidth = pdfCanvas.width;
  const pdfCanvasHeight = pdfCanvas.height;
  const canvasWidth = canvas.width;
  const canvasHeight = canvas.height;
  
  // 获取PDF canvas的显示尺寸（CSS尺寸，可能受样式影响）
  const pdfDisplayWidth = pdfCanvas.offsetWidth || pdfCanvasWidth;
  const pdfDisplayHeight = pdfCanvas.offsetHeight || pdfCanvasHeight;
  
  // 计算坐标比例
  const scaleX = canvasWidth / pdfDisplayWidth;
  const scaleY = canvasHeight / pdfDisplayHeight;
  
  // 转换为canvas坐标
  const x = unscaledX * scaleX;
  const y = unscaledY * scaleY;
  
  // 确保坐标在canvas范围内
  return {
    x: Math.max(0, Math.min(canvasWidth, x)),
    y: Math.max(0, Math.min(canvasHeight, y)),
  };
};

const getNormalizedCoordinates = (x, y) => {
  if (!canvasRef.value) return { x: 0, y: 0 };
  return {
    x: x / canvasRef.value.width,
    y: y / canvasRef.value.height,
  };
};

const getAbsoluteCoordinates = (normalized) => {
  if (!canvasRef.value) return { x: 0, y: 0 };
  return {
    x: normalized.x * canvasRef.value.width,
    y: normalized.y * canvasRef.value.height,
  };
};

const onMouseDown = (event) => {
  if (tool.value === 'move') {
    isDragging.value = true;
    dragStart.value = { x: event.clientX, y: event.clientY };
    dragStartTranslate.value = { x: translateX.value, y: translateY.value };
    return;
  }
  
  if (tool.value === 'select-text') {
    const coords = getCanvasCoordinates(event);
    const absCoords = getAbsoluteCoordinates(getNormalizedCoordinates(coords.x, coords.y));
    
    // 检查是否点击在文本框上
    for (let i = elements.value.length - 1; i >= 0; i--) {
      const element = elements.value[i];
      if (element.type === 'text') {
        const absX = getAbsoluteCoordinates({ x: element.x, y: element.y }).x;
        const absY = getAbsoluteCoordinates({ x: element.x, y: element.y }).y;
        const absWidth = element.width * canvasRef.value.width;
        const absHeight = element.height * canvasRef.value.height;
        
        if (coords.x >= absX && coords.x <= absX + absWidth &&
            coords.y >= absY && coords.y <= absY + absHeight) {
          selectedTextIndex.value = i;
          
          // 检查是否点击在缩放控制点上
          const handle = getResizeHandle(coords.x, coords.y, absX, absY, absWidth, absHeight);
          if (handle) {
            isResizingText.value = true;
            textResizeHandle.value = handle;
            textResizeStart.value = {
              x: absX,
              y: absY,
              width: absWidth,
              height: absHeight,
            };
            textDragStart.value = { x: event.clientX, y: event.clientY };
          } else {
            isDraggingText.value = true;
            textDragStart.value = { x: event.clientX, y: event.clientY };
          }
          redraw();
          return;
        }
      }
    }
    
    selectedTextIndex.value = -1;
    redraw();
    return;
  }
  
  if (tool.value === 'text') {
    const coords = getCanvasCoordinates(event);
    textPosition.value = coords;
    showTextDialog.value = true;
    return;
  }
  
  if (tool.value.startsWith('pen-')) {
    isDrawing.value = true;
    const coords = getCanvasCoordinates(event);
    currentPath.value = [coords];
  }
};

const getResizeHandle = (x, y, elemX, elemY, elemWidth, elemHeight) => {
  const handleSize = 8;
  const handles = [
    { name: 'nw', x: elemX, y: elemY },
    { name: 'ne', x: elemX + elemWidth, y: elemY },
    { name: 'sw', x: elemX, y: elemY + elemHeight },
    { name: 'se', x: elemX + elemWidth, y: elemY + elemHeight },
    { name: 'n', x: elemX + elemWidth / 2, y: elemY },
    { name: 's', x: elemX + elemWidth / 2, y: elemY + elemHeight },
    { name: 'w', x: elemX, y: elemY + elemHeight / 2 },
    { name: 'e', x: elemX + elemWidth, y: elemY + elemHeight / 2 },
  ];
  
  for (const handle of handles) {
    if (Math.abs(x - handle.x) < handleSize && Math.abs(y - handle.y) < handleSize) {
      return handle.name;
    }
  }
  return '';
};

const onMouseMove = (event) => {
  if (tool.value === 'move' && isDragging.value) {
    const deltaX = event.clientX - dragStart.value.x;
    const deltaY = event.clientY - dragStart.value.y;
    translateX.value = dragStartTranslate.value.x + deltaX;
    translateY.value = dragStartTranslate.value.y + deltaY;
    return;
  }
  
  if (tool.value === 'select-text' && isDraggingText.value && selectedTextIndex.value >= 0) {
    const currentElements = [...elements.value];
    const element = currentElements[selectedTextIndex.value];
    const deltaX = (event.clientX - textDragStart.value.x) / scale.value;
    const deltaY = (event.clientY - textDragStart.value.y) / scale.value;
    
    const absCoords = getAbsoluteCoordinates({ x: element.x, y: element.y });
    const newAbsX = absCoords.x + deltaX;
    const newAbsY = absCoords.y + deltaY;
    
    // 创建新对象，确保响应式更新
    currentElements[selectedTextIndex.value] = {
      ...element,
      x: getNormalizedCoordinates(newAbsX, newAbsY).x,
      y: getNormalizedCoordinates(newAbsX, newAbsY).y,
    };
    elements.value = currentElements;
    
    textDragStart.value = { x: event.clientX, y: event.clientY };
    redraw();
    return;
  }
  
  if (tool.value === 'select-text' && isResizingText.value && selectedTextIndex.value >= 0) {
    const currentElements = [...elements.value];
    const element = currentElements[selectedTextIndex.value];
    const start = textResizeStart.value;
    const deltaX = (event.clientX - textDragStart.value.x) / scale.value;
    const deltaY = (event.clientY - textDragStart.value.y) / scale.value;
    
    let newX = element.x;
    let newY = element.y;
    let newWidth = element.width * canvasRef.value.width;
    let newHeight = element.height * canvasRef.value.height;
    
    const handle = textResizeHandle.value;
    if (handle.includes('e')) {
      newWidth = Math.max(20, start.width + deltaX);
    }
    if (handle.includes('w')) {
      newWidth = Math.max(20, start.width - deltaX);
      const oldPos = getAbsoluteCoordinates({ x: element.x, y: element.y });
      const newPosX = oldPos.x - (newWidth - start.width);
      newX = getNormalizedCoordinates(newPosX, oldPos.y).x;
    }
    if (handle.includes('s')) {
      newHeight = Math.max(16, start.height + deltaY);
    }
    if (handle.includes('n')) {
      newHeight = Math.max(16, start.height - deltaY);
      const oldPos = getAbsoluteCoordinates({ x: element.x, y: element.y });
      const newPosY = oldPos.y - (newHeight - start.height);
      newY = getNormalizedCoordinates(oldPos.x, newPosY).y;
    }
    
    // 归一化宽度和高度
    newWidth = newWidth / canvasRef.value.width;
    newHeight = newHeight / canvasRef.value.height;
    
    // 创建新对象，确保响应式更新
    currentElements[selectedTextIndex.value] = {
      ...element,
      x: newX,
      y: newY,
      width: newWidth,
      height: newHeight,
    };
    elements.value = currentElements;
    redraw();
    return;
  }
  
  if (!isDrawing.value || !tool.value.startsWith('pen-')) return;
  
  const coords = getCanvasCoordinates(event);
  currentPath.value.push(coords);
  drawPath(currentPath.value, tool.value === 'pen-red' ? '#ff0000' : '#0000ff');
};

const onMouseUp = () => {
  if (tool.value === 'move' && isDragging.value) {
    isDragging.value = false;
    return;
  }
  
  if (tool.value === 'select-text' && (isDraggingText.value || isResizingText.value)) {
    if (isDraggingText.value || isResizingText.value) {
      // 保存当前页面的历史
      history.value.push({
        page: currentPage.value,
        elements: JSON.parse(JSON.stringify(elements.value))
      });
    }
    isDraggingText.value = false;
    isResizingText.value = false;
    textResizeHandle.value = '';
    redraw();
    return;
  }
  
  if (!isDrawing.value) return;
  
  if (currentPath.value.length > 0) {
    history.value.push(JSON.parse(JSON.stringify(elements.value)));
    
    const normalizedPath = currentPath.value.map(point => 
      getNormalizedCoordinates(point.x, point.y)
    );
    
    // 确保通过 setter 更新，触发响应式
    const currentElements = [...elements.value];
    currentElements.push({
      type: 'path',
      color: tool.value === 'pen-red' ? '#ff0000' : '#0000ff',
      points: normalizedPath,
    });
    elements.value = currentElements;
  }
  
  isDrawing.value = false;
  currentPath.value = [];
  redraw();
};

const drawPath = (path, color) => {
  if (!canvasRef.value || path.length < 2) return;
  
  const ctx = canvasRef.value.getContext('2d');
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  
  ctx.beginPath();
  ctx.moveTo(path[0].x, path[0].y);
  for (let i = 1; i < path.length; i++) {
    ctx.lineTo(path[i].x, path[i].y);
  }
  ctx.stroke();
};

const redraw = () => {
  if (!canvasRef.value) return;
  
  const ctx = canvasRef.value.getContext('2d');
  ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
  
  // 绘制所有元素
  elements.value.forEach((element, index) => {
    if (element.type === 'path') {
      drawElementPath(element);
    } else if (element.type === 'text') {
      drawElementText(element, index === selectedTextIndex.value);
    }
  });
  
  // 绘制当前路径
  if (currentPath.value.length > 0) {
    drawPath(currentPath.value, tool.value === 'pen-red' ? '#ff0000' : '#0000ff');
  }
};

const drawElementPath = (element) => {
  if (!canvasRef.value || !element.points || element.points.length < 2) return;
  
  const ctx = canvasRef.value.getContext('2d');
  ctx.strokeStyle = element.color || '#000000';
  ctx.lineWidth = 2;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  
  ctx.beginPath();
  const firstPoint = getAbsoluteCoordinates(element.points[0]);
  ctx.moveTo(firstPoint.x, firstPoint.y);
  for (let i = 1; i < element.points.length; i++) {
    const point = getAbsoluteCoordinates(element.points[i]);
    ctx.lineTo(point.x, point.y);
  }
  ctx.stroke();
};

const drawElementText = (element, isSelected) => {
  const textContent = element.text || element.content || '';
  if (!canvasRef.value || !textContent) return;
  
  const ctx = canvasRef.value.getContext('2d');
  const absX = getAbsoluteCoordinates({ x: element.x, y: element.y }).x;
  const absY = getAbsoluteCoordinates({ x: element.x, y: element.y }).y;
  const absWidth = element.width * canvasRef.value.width;
  const absHeight = element.height * canvasRef.value.height;
  
  // 绘制背景框
  ctx.fillStyle = element.boxColor || boxColor.value;
  ctx.globalAlpha = (element.boxOpacity !== undefined ? element.boxOpacity : boxOpacity.value) / 100;
  ctx.fillRect(absX, absY, absWidth, absHeight);
  ctx.globalAlpha = 1;
  
  // 绘制边框
  if (isSelected) {
    ctx.strokeStyle = '#409EFF';
    ctx.lineWidth = 2;
    ctx.strokeRect(absX, absY, absWidth, absHeight);
    
    // 绘制缩放控制点
    const handleSize = 8;
    const handles = [
      { x: absX, y: absY },
      { x: absX + absWidth, y: absY },
      { x: absX, y: absY + absHeight },
      { x: absX + absWidth, y: absY + absHeight },
      { x: absX + absWidth / 2, y: absY },
      { x: absX + absWidth / 2, y: absY + absHeight },
      { x: absX, y: absY + absHeight / 2 },
      { x: absX + absWidth, y: absY + absHeight / 2 },
    ];
    
    ctx.fillStyle = '#409EFF';
    handles.forEach(handle => {
      ctx.fillRect(handle.x - handleSize / 2, handle.y - handleSize / 2, handleSize, handleSize);
    });
  }
  
  // 绘制文本
  ctx.fillStyle = element.textColor || element.color || textColor.value;
  ctx.font = `${absHeight * 0.6}px Arial`;
  ctx.textBaseline = 'top';
  ctx.fillText(textContent, absX + 4, absY + 4);
};

const undo = () => {
  if (history.value.length === 0) return;
  isUndoing = true;
  const lastState = history.value.pop();
  if (lastState && lastState.page === currentPage.value) {
    // 只恢复当前页面的历史
    elements.value = lastState.elements;
  } else if (lastState) {
    // 如果是其他页面的历史，放回去
    history.value.push(lastState);
  }
  redraw();
  nextTick(() => {
    isUndoing = false;
  });
};

const clear = () => {
  if (elements.value.length === 0) return;
  // 只保存当前页面的历史
  history.value.push({
    page: currentPage.value,
    elements: JSON.parse(JSON.stringify(elements.value))
  });
  elements.value = [];
  redraw();
};

const confirmTextInput = () => {
  if (!textInput.value.trim()) {
    showTextDialog.value = false;
    return;
  }
  
  // 保存当前页面的历史
  history.value.push({
    page: currentPage.value,
    elements: JSON.parse(JSON.stringify(elements.value))
  });
  
  const normalized = getNormalizedCoordinates(textPosition.value.x, textPosition.value.y);
  // 创建新数组，确保触发 setter
  const currentElements = [...elements.value];
  currentElements.push({
    type: 'text',
    x: normalized.x,
    y: normalized.y,
    width: 0.2,
    height: 0.1,
    text: textInput.value,
    content: textInput.value, // 兼容ImageAnnotator的content字段
    textColor: textColor.value,
    boxColor: boxColor.value,
    boxOpacity: boxOpacity.value,
  });
  elements.value = currentElements; // 触发更新
  
  textInput.value = '';
  showTextDialog.value = false;
  redraw();
};

const cancelTextInput = () => {
  textInput.value = '';
  showTextDialog.value = false;
};

// 监听PDF URL变化
watch(() => props.pdfUrl, (newUrl, oldUrl) => {
  // 如果URL变化，先清理旧的PDF
  if (oldUrl && oldUrl !== newUrl) {
    cleanupPDF();
  }
  if (newUrl) {
    loadPDF();
  }
}, { immediate: true });

onMounted(() => {
  if (props.pdfUrl) {
    loadPDF();
  }
});

// 组件卸载前清理PDF文档
onBeforeUnmount(() => {
  cleanupPDF();
});
</script>

<style scoped>
.pdf-annotator {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f5f7fa;
}

.annotator-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  flex-wrap: wrap;
  gap: 12px;
}

.page-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-info {
  font-size: 14px;
  color: #606266;
  min-width: 60px;
  text-align: center;
}

.annotator-content {
  flex: 1;
  overflow: hidden;
  position: relative;
  background: #e4e7ed;
}

.pdf-wrapper {
  position: relative;
  display: inline-block;
}

.pdf-canvas {
  display: block;
  background: white;
}

.annotation-canvas {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: auto;
  cursor: crosshair;
}

.annotation-canvas.move-cursor {
  cursor: move;
}

.annotation-canvas.readonly-canvas {
  pointer-events: none;
}
</style>

