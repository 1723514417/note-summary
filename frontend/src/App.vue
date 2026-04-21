<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="sidebar-brand">📝 Note Summary</div>
      <ul class="sidebar-nav">
        <li>
          <router-link to="/" exact-active-class="router-link-active">
            <span>✏️</span> 记录
          </router-link>
        </li>
        <li>
          <router-link to="/search" active-class="router-link-active">
            <span>🔍</span> 搜索
          </router-link>
        </li>
        <li>
          <router-link to="/categories" active-class="router-link-active">
            <span>📁</span> 分类
          </router-link>
        </li>
      </ul>
    </aside>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>
