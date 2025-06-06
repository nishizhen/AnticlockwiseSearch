<script setup>
import { ref } from 'vue';
import axios from 'axios'; // 使用 axios 发送 HTTP 请求

const searchQuery = ref('');
const searchResults = ref([]);
const isLoading = ref(false);
const error = ref(null);

// 运行时获取API基础URL
const getApiBaseUrl = () => {
  // 首先尝试从window对象获取（可以通过index.html注入）
  if (window.VITE_API_BASE_URL) {
    return window.VITE_API_BASE_URL;
  }
  
  // 然后尝试从构建时的环境变量获取
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // 最后使用默认值
  return 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();
console.log('Using API_BASE_URL:', API_BASE_URL); // 添加调试日志

async function performSearch() {
    if (!searchQuery.value.trim()) {
        searchResults.value = [];
        return;
    }

    isLoading.value = true;
    error.value = null;
    try {
        const response = await axios.get(`${API_BASE_URL}/search`, {
            params: { query: searchQuery.value },
            timeout: 15000 // 15秒超时
        });
        searchResults.value = response.data;
    } catch (err) {
        console.error('Search failed:', err);
        if (axios.isAxiosError(err)) {
            if (err.response) {
                error.value = `搜索失败: ${err.response.status} - ${err.response.data.detail || err.response.statusText}`;
            } else if (err.request) {
                error.value = '搜索请求无响应，请检查后端服务是否运行或网络连接。';
            } else {
                error.value = '搜索请求配置错误。';
            }
        } else {
            error.value = '发生未知错误。';
        }
    } finally {
        isLoading.value = false;
    }
}
</script>

<template>
    <div class="container">
        <h1>AnticlockwiseSearch</h1>
        <div class="search-box">
            <input 
                type="text" 
                v-model="searchQuery" 
                @keyup.enter="performSearch" 
                placeholder="输入关键字搜索..."
            />
            <button @click="performSearch" :disabled="isLoading">搜索</button>
        </div>

        <p v-if="isLoading">正在搜索...</p>
        <p v-if="error" class="error-message">{{ error }}</p>

        <div class="results" v-if="searchResults.length > 0">
            <div v-for="result in searchResults" :key="result.source + '-' + result.id" class="result-item">
                <div class="source-tag">{{ result.source }}</div>
                <img v-if="result.thumbnail_url" :src="result.thumbnail_url" alt="Thumbnail" class="thumbnail" />
                <div class="content">
                    <h3>
                        <a :href="result.detail_url" target="_blank" rel="noopener noreferrer">
                            {{ result.title }}
                        </a>
                    </h3>
                    <p v-if="result.description">{{ result.description }}</p>
                    <span v-if="result.type" class="type-tag">{{ result.type }}</span>
                </div>
            </div>
        </div>
        <p v-else-if="!isLoading && searchQuery.length > 0">没有找到相关结果。</p>
    </div>
</template>
