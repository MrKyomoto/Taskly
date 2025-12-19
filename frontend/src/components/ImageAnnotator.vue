<template>
  <div class="image-annotator">
    <div class="annotator-toolbar" v-if="!readonly">
      <el-button-group>
        <el-button 
          :type="tool === 'move' ? 'primary' : 'default'"
          @click="setTool('move')"
          size="small"
          title="移动图片"
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
      </el-button-group>
    </div>
    
    <div class="annotator-content" v-if="imageUrl" ref="contentRef" @wheel.prevent="onWheel">
      <div 
        class="image-wrapper" 
        ref="imageWrapperRef"
        :style="{
          transform: `translate(${translateX}px, ${translateY}px) scale(${scale})`,
          transformOrigin: '0 0'
        }"
      >
        <img 
          :src="getImageUrl(imageUrl)" 
          ref="imageRef"
          @load="onImageLoad"
          class="annotation-image"
          draggable="false"
        />
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
      <!-- 悬浮工具栏 -->
      <div class="floating-toolbar" v-if="!readonly">
        <div class="floating-toolbar-inner">
          <el-button-group>
            <el-button 
              :type="tool === 'move' ? 'primary' : 'default'"
              @click="setTool('move')"
              size="small"
              title="移动图片"
            >
              <el-icon><Rank /></el-icon>
            </el-button>
            <el-button 
              :type="tool === 'pen-red' ? 'primary' : 'default'"
              @click="setTool('pen-red')"
              size="small"
              title="红笔"
            >
              <el-icon><EditPen /></el-icon>
            </el-button>
            <el-button 
              :type="tool === 'pen-blue' ? 'primary' : 'default'"
              @click="setTool('pen-blue')"
              size="small"
              title="蓝笔"
            >
              <el-icon><EditPen /></el-icon>
            </el-button>
            <el-button 
              :type="tool === 'text' ? 'primary' : 'default'"
              @click="setTool('text')"
              size="small"
              title="文本批注"
            >
              <el-icon><Document /></el-icon>
            </el-button>
            <el-button 
              :type="tool === 'select-text' ? 'primary' : 'default'"
              @click="setTool('select-text')"
              size="small"
              title="选择文本"
            >
              <el-icon><Pointer /></el-icon>
            </el-button>
            <el-button 
              @click="undo"
              size="small"
              :disabled="history.length === 0"
              title="撤销"
            >
              <el-icon><RefreshLeft /></el-icon>
            </el-button>
            <el-button 
              @click="clear"
              size="small"
              :disabled="elements.length === 0"
              title="清空"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </el-button-group>
          <div class="zoom-controls">
            <el-button 
              @click="zoomOut"
              size="small"
              :disabled="scale <= 0.1"
            >
              <el-icon><ZoomOut /></el-icon>
            </el-button>
            <span class="zoom-value">{{ Math.round(scale * 100) }}%</span>
            <el-button 
              @click="zoomIn"
              size="small"
              :disabled="scale >= 5"
            >
              <el-icon><ZoomIn /></el-icon>
            </el-button>
            <el-button 
              @click="resetView"
              size="small"
            >
              重置
            </el-button>
          </div>
        </div>
      </div>
    </div>
    <el-empty v-else description="暂无图片" :image-size="100" />
    
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
import { ref, watch, nextTick, onMounted } from 'vue';
import { EditPen, Document, RefreshLeft, Delete, Rank, ZoomIn, ZoomOut, Pointer } from '@element-plus/icons-vue';
import { getImageUrl } from '@/utils/image';

const props = defineProps({
  imageUrl: {
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

const imageRef = ref(null);
const canvasRef = ref(null);
const imageWrapperRef = ref(null);
const contentRef = ref(null);
const textInputRef = ref(null);
const showTextDialog = ref(false);
const textInput = ref('');
const textPosition = ref({ x: 0, y: 0 });
const textColor = ref('#000000'); // 文本颜色
const boxColor = ref('#ffffff'); // 框体颜色
const boxOpacity = ref(80); // 框体透明度（0-100）

const tool = ref('move'); // 默认工具改为移动
const isDrawing = ref(false);
const currentPath = ref([]);

// 缩放和拖动相关
const scale = ref(1);
const translateX = ref(0);
const translateY = ref(0);
const isDragging = ref(false);
const dragStart = ref({ x: 0, y: 0 });
const dragStartTranslate = ref({ x: 0, y: 0 });
const elements = ref([]);
const history = ref([]);

// 文本选择和编辑相关
const selectedTextIndex = ref(-1); // 当前选中的文本元素索引
const isDraggingText = ref(false); // 是否正在拖动文本框
const isResizingText = ref(false); // 是否正在缩放文本框
const textDragStart = ref({ x: 0, y: 0 }); // 拖动起始位置
const textResizeHandle = ref(''); // 缩放控制点位置（'nw', 'ne', 'sw', 'se', 'n', 's', 'w', 'e'）
const textResizeStart = ref({ x: 0, y: 0, width: 0, height: 0 }); // 缩放起始状态

// 监听 modelValue 变化，回显批注
let isUpdatingFromProps = false;
let isUndoing = false; // 标记是否正在撤销操作
watch(() => props.modelValue, (newValue) => {
  if (isUpdatingFromProps || isUndoing) return; // 避免循环更新和撤销时的更新
  if (newValue && newValue.elements) {
    const newElements = JSON.parse(JSON.stringify(newValue.elements));
    // 检查是否真的需要更新
    if (JSON.stringify(elements.value) !== JSON.stringify(newElements)) {
      elements.value = newElements;
      // 当从外部更新时，清空历史记录（因为这是新的状态）
      history.value = [];
      nextTick(() => {
        redraw();
      });
    }
  }
}, { deep: true, immediate: true });

// 监听 elements 变化，更新 modelValue
watch(elements, (newElements) => {
  if (isUpdatingFromProps || isUndoing) return; // 避免循环更新和撤销时的更新
  isUpdatingFromProps = true;
  const newValue = {
    version: 1,
    elements: JSON.parse(JSON.stringify(newElements)),
  };
  // 检查是否真的需要更新
  const currentValue = props.modelValue;
  if (!currentValue || JSON.stringify(currentValue) !== JSON.stringify(newValue)) {
    emit('update:modelValue', newValue);
  }
  nextTick(() => {
    isUpdatingFromProps = false;
  });
}, { deep: true, flush: 'post' });

const setTool = (newTool) => {
  tool.value = newTool;
  // 切换工具时停止绘制和拖动
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

// 缩放功能
const zoomIn = () => {
  if (scale.value < 5) {
    scale.value = Math.min(5, scale.value + 0.1);
  }
};

const zoomOut = () => {
  if (scale.value > 0.1) {
    scale.value = Math.max(0.1, scale.value - 0.1);
  }
};

// 鼠标滚轮缩放
const onWheel = (event) => {
  if (props.readonly) return;
  
  event.preventDefault();
  const delta = event.deltaY > 0 ? -0.1 : 0.1;
  const newScale = Math.max(0.1, Math.min(5, scale.value + delta));
  scale.value = newScale;
};

// 重置视图
const resetView = () => {
  scale.value = 1;
  translateX.value = 0;
  translateY.value = 0;
};

const onImageLoad = () => {
  nextTick(() => {
    setupCanvas();
    redraw();
  });
};

const setupCanvas = () => {
  if (!canvasRef.value || !imageRef.value) return;
  
  const canvas = canvasRef.value;
  const image = imageRef.value;
  
  // 设置 Canvas 实际尺寸（重要：必须与图片实际显示尺寸一致）
  canvas.width = image.clientWidth;
  canvas.height = image.clientHeight;
  
  // 设置 Canvas 显示尺寸
  canvas.style.width = `${image.clientWidth}px`;
  canvas.style.height = `${image.clientHeight}px`;
};

const getCanvasCoordinates = (event) => {
  if (!canvasRef.value || !imageWrapperRef.value || !imageRef.value) return { x: 0, y: 0 };
  
  const canvas = canvasRef.value;
  const wrapper = imageWrapperRef.value;
  const image = imageRef.value;
  const rect = wrapper.getBoundingClientRect();
  
  // 考虑缩放和位移，计算相对于图片的坐标
  const x = (event.clientX - rect.left - translateX.value) / scale.value;
  const y = (event.clientY - rect.top - translateY.value) / scale.value;
  
  // 转换为 canvas 坐标（canvas 尺寸与图片显示尺寸一致）
  // canvas.width 和 canvas.height 已经设置为 image.clientWidth 和 image.clientHeight
  const scaleX = canvas.width / image.clientWidth;
  const scaleY = canvas.height / image.clientHeight;
  
  return {
    x: x * scaleX,
    y: y * scaleY,
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

// 检查点击位置是否在文本框内或控制点上
const getTextElementAtPoint = (x, y) => {
  if (!canvasRef.value) return null;
  const ctx = canvasRef.value.getContext('2d');
  
  for (let i = elements.value.length - 1; i >= 0; i--) {
    const element = elements.value[i];
    if (element.type === 'text') {
      const pos = getAbsoluteCoordinates({ x: element.x, y: element.y });
      ctx.font = '16px Arial';
      const textMetrics = ctx.measureText(element.content);
      const textWidth = element.width || textMetrics.width;
      const textHeight = element.height || 20;
      const padding = 4;
      
      const boxX = pos.x - padding;
      const boxY = pos.y - textHeight - padding;
      const boxWidth = textWidth + padding * 2;
      const boxHeight = textHeight + padding * 2;
      
      if (x >= boxX && x <= boxX + boxWidth && y >= boxY && y <= boxY + boxHeight) {
        return { index: i, element, boxX, boxY, boxWidth, boxHeight };
      }
    }
  }
  return null;
};

// 获取缩放控制点位置
const getResizeHandle = (x, y, boxX, boxY, boxWidth, boxHeight) => {
  const handleSize = 8;
  const handles = [
    { name: 'nw', x: boxX, y: boxY },
    { name: 'ne', x: boxX + boxWidth, y: boxY },
    { name: 'sw', x: boxX, y: boxY + boxHeight },
    { name: 'se', x: boxX + boxWidth, y: boxY + boxHeight },
    { name: 'n', x: boxX + boxWidth / 2, y: boxY },
    { name: 's', x: boxX + boxWidth / 2, y: boxY + boxHeight },
    { name: 'w', x: boxX, y: boxY + boxHeight / 2 },
    { name: 'e', x: boxX + boxWidth, y: boxY + boxHeight / 2 },
  ];
  
  for (const handle of handles) {
    if (Math.abs(x - handle.x) <= handleSize && Math.abs(y - handle.y) <= handleSize) {
      return handle.name;
    }
  }
  return null;
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
    const textInfo = getTextElementAtPoint(coords.x, coords.y);
    
    if (textInfo) {
      // 检查是否点击了缩放控制点
      const handle = getResizeHandle(coords.x, coords.y, textInfo.boxX, textInfo.boxY, textInfo.boxWidth, textInfo.boxHeight);
      if (handle) {
        // 开始缩放
        isResizingText.value = true;
        textResizeHandle.value = handle;
        selectedTextIndex.value = textInfo.index;
        const element = textInfo.element;
        const ctx = canvasRef.value.getContext('2d');
        ctx.font = '16px Arial';
        const textWidth = element.width || ctx.measureText(element.content).width;
        const textHeight = element.height || 20;
        textResizeStart.value = {
          x: coords.x,
          y: coords.y,
          width: textWidth,
          height: textHeight,
          elementX: element.x,
          elementY: element.y,
        };
      } else {
        // 开始拖动文本框
        isDraggingText.value = true;
        selectedTextIndex.value = textInfo.index;
        textDragStart.value = {
          x: coords.x,
          y: coords.y,
          elementX: textInfo.element.x,
          elementY: textInfo.element.y,
        };
      }
    } else {
      // 点击空白处，取消选择
      selectedTextIndex.value = -1;
    }
    redraw(); // 重绘以显示选中框
    return;
  }
  
  if (tool.value === 'text') {
    const coords = getCanvasCoordinates(event);
    const normalized = getNormalizedCoordinates(coords.x, coords.y);
    textPosition.value = normalized;
    showTextDialog.value = true;
    nextTick(() => {
      textInputRef.value?.focus();
    });
    return;
  }
  
  if (tool.value.startsWith('pen-')) {
    isDrawing.value = true;
    const coords = getCanvasCoordinates(event);
    currentPath.value = [coords];
  }
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
    const coords = getCanvasCoordinates(event);
    const deltaX = coords.x - textDragStart.value.x;
    const deltaY = coords.y - textDragStart.value.y;
    
    const element = elements.value[selectedTextIndex.value];
    const oldPos = getAbsoluteCoordinates({ x: textDragStart.value.elementX, y: textDragStart.value.elementY });
    const newPos = { x: oldPos.x + deltaX, y: oldPos.y + deltaY };
    const normalized = getNormalizedCoordinates(newPos.x, newPos.y);
    
    element.x = normalized.x;
    element.y = normalized.y;
    redraw();
    return;
  }
  
  if (tool.value === 'select-text' && isResizingText.value && selectedTextIndex.value >= 0) {
    const coords = getCanvasCoordinates(event);
    const element = elements.value[selectedTextIndex.value];
    const handle = textResizeHandle.value;
    const start = textResizeStart.value;
    
    let deltaX = coords.x - start.x;
    let deltaY = coords.y - start.y;
    
    // 根据控制点位置计算新的宽度和高度
    let newWidth = start.width;
    let newHeight = start.height;
    let newX = start.elementX;
    let newY = start.elementY;
    
    if (handle.includes('e')) {
      newWidth = Math.max(20, start.width + deltaX);
    }
    if (handle.includes('w')) {
      newWidth = Math.max(20, start.width - deltaX);
      const oldPos = getAbsoluteCoordinates({ x: start.elementX, y: start.elementY });
      const newPosX = oldPos.x - (newWidth - start.width);
      newX = getNormalizedCoordinates(newPosX, oldPos.y).x;
    }
    if (handle.includes('s')) {
      newHeight = Math.max(16, start.height + deltaY);
    }
    if (handle.includes('n')) {
      newHeight = Math.max(16, start.height - deltaY);
      const oldPos = getAbsoluteCoordinates({ x: start.elementX, y: start.elementY });
      const newPosY = oldPos.y - (newHeight - start.height);
      newY = getNormalizedCoordinates(oldPos.x, newPosY).y;
    }
    
    element.x = newX;
    element.y = newY;
    element.width = newWidth;
    element.height = newHeight;
    redraw();
    return;
  }
  
  if (!isDrawing.value || !tool.value.startsWith('pen-')) return;
  
  const coords = getCanvasCoordinates(event);
  currentPath.value.push(coords);
  
  // 实时绘制
  drawPath(currentPath.value, tool.value === 'pen-red' ? '#ff0000' : '#0000ff');
};

const onMouseUp = () => {
  if (tool.value === 'move' && isDragging.value) {
    isDragging.value = false;
    return;
  }
  
  if (tool.value === 'select-text' && (isDraggingText.value || isResizingText.value)) {
    if (isDraggingText.value || isResizingText.value) {
      // 保存到历史记录
      history.value.push(JSON.parse(JSON.stringify(elements.value)));
      emit('update:modelValue', {
        version: 1,
        elements: JSON.parse(JSON.stringify(elements.value)),
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
    // 保存到历史记录
    history.value.push(JSON.parse(JSON.stringify(elements.value)));
    
    // 转换为归一化坐标
    const normalizedPath = currentPath.value.map(point => 
      getNormalizedCoordinates(point.x, point.y)
    );
    
    // 添加到元素列表
    elements.value.push({
      type: 'path',
      color: tool.value === 'pen-red' ? '#ff0000' : '#0000ff',
      points: normalizedPath,
    });
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
  
  elements.value.forEach(element => {
    if (element.type === 'path') {
      const path = element.points.map(point => getAbsoluteCoordinates(point));
      drawPath(path, element.color);
    } else if (element.type === 'text') {
      const pos = getAbsoluteCoordinates({ x: element.x, y: element.y });
      
      // 测量文本尺寸
      ctx.font = '16px Arial';
      const textMetrics = ctx.measureText(element.content);
      const textWidth = element.width || textMetrics.width;
      const textHeight = element.height || 20;
      const padding = 4;
      
      const boxX = pos.x - padding;
      const boxY = pos.y - textHeight - padding;
      const boxWidth = textWidth + padding * 2;
      const boxHeight = textHeight + padding * 2;
      
      // 绘制框体背景（如果有）
      if (element.boxColor) {
        const opacity = (element.boxOpacity !== undefined ? element.boxOpacity : 80) / 100;
        ctx.fillStyle = element.boxColor;
        ctx.globalAlpha = opacity;
        ctx.fillRect(boxX, boxY, boxWidth, boxHeight);
        ctx.globalAlpha = 1;
      }
      
      // 绘制文本
      ctx.fillStyle = element.textColor || element.color || '#000000';
      ctx.font = '16px Arial';
      ctx.fillText(element.content, pos.x, pos.y);
      
      // 如果选中，绘制选中框和缩放控制点
      const isSelected = selectedTextIndex.value === i && tool.value === 'select-text';
      if (isSelected) {
        // 绘制选中框边框
        ctx.strokeStyle = '#409EFF';
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);
        ctx.strokeRect(boxX, boxY, boxWidth, boxHeight);
        ctx.setLineDash([]);
        
        // 绘制缩放控制点
        const handleSize = 8;
        const handles = [
          { x: boxX, y: boxY },
          { x: boxX + boxWidth, y: boxY },
          { x: boxX, y: boxY + boxHeight },
          { x: boxX + boxWidth, y: boxY + boxHeight },
          { x: boxX + boxWidth / 2, y: boxY },
          { x: boxX + boxWidth / 2, y: boxY + boxHeight },
          { x: boxX, y: boxY + boxHeight / 2 },
          { x: boxX + boxWidth, y: boxY + boxHeight / 2 },
        ];
        
        ctx.fillStyle = '#409EFF';
        handles.forEach(handle => {
          ctx.fillRect(handle.x - handleSize / 2, handle.y - handleSize / 2, handleSize, handleSize);
        });
      }
    }
  });
};

const confirmTextInput = () => {
  if (!textInput.value.trim()) {
    showTextDialog.value = false;
    return;
  }
  
  // 保存到历史记录
  history.value.push(JSON.parse(JSON.stringify(elements.value)));
  
  // 添加文本元素（包含框体和文本颜色）
  elements.value.push({
    type: 'text',
    x: textPosition.value.x,
    y: textPosition.value.y,
    content: textInput.value,
    color: textColor.value, // 文本颜色（向后兼容）
    textColor: textColor.value, // 文本颜色
    boxColor: boxColor.value, // 框体颜色
    boxOpacity: boxOpacity.value, // 框体透明度
  });
  
  textInput.value = '';
  showTextDialog.value = false;
  nextTick(() => {
    redraw();
  });
};

const cancelTextInput = () => {
  textInput.value = '';
  showTextDialog.value = false;
  // 重置颜色为默认值
  textColor.value = '#000000';
  boxColor.value = '#ffffff';
  boxOpacity.value = 80;
};

const undo = () => {
  if (history.value.length === 0) return;
  
  isUndoing = true;
  const previousState = history.value.pop();
  if (previousState) {
    // 直接设置 elements，不触发 watch
    elements.value = JSON.parse(JSON.stringify(previousState));
    // 手动触发更新到父组件（但需要延迟，避免 watch 拦截）
    nextTick(() => {
      redraw();
      // 延迟重置标志，确保 watch 不会触发
      setTimeout(() => {
        isUndoing = false;
        // 手动触发一次更新，确保父组件同步
        const newValue = {
          version: 1,
          elements: JSON.parse(JSON.stringify(elements.value)),
        };
        emit('update:modelValue', newValue);
      }, 0);
    });
  } else {
    isUndoing = false;
  }
};

const clear = () => {
  if (elements.value.length === 0) return;
  
  history.value.push(JSON.parse(JSON.stringify(elements.value)));
  elements.value = [];
  nextTick(() => {
    redraw();
  });
};

onMounted(() => {
  if (imageRef.value?.complete) {
    onImageLoad();
  }
});
</script>

<style scoped>
.image-annotator {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.annotator-content {
  position: relative;
  flex: 1;
  overflow: hidden;
  background: #0f172a;
}

.image-wrapper {
  position: relative;
  display: inline-block;
  cursor: move;
  transition: transform 0.1s;
}

.annotation-image {
  display: block;
  max-width: 100%;
  height: auto;
  user-select: none;
}

.annotation-canvas {
  position: absolute;
  top: 0;
  left: 0;
  cursor: crosshair;
  user-select: none;
}

.annotation-canvas.readonly-canvas {
  cursor: default;
  pointer-events: none;
}

.annotation-canvas.move-cursor {
  cursor: move;
}

.floating-toolbar {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}

.floating-toolbar-inner {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.92);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.5);
}

.floating-toolbar-inner .el-button {
  border: none;
}

.floating-toolbar-inner .el-button--primary {
  background-color: #3b82f6;
}

.zoom-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.zoom-value {
  min-width: 50px;
  text-align: center;
  font-size: 14px;
}
</style>

