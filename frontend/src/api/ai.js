import { request } from './index';

/**
 * AI 生成批改反馈
 * @param {Object} data - 包含 text_content 字段
 */
export const generateAIFeedback = (data) =>
  request.post('/ai/generate-feedback', data);

