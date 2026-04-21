<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="sidebar-brand">📝 <span class="nav-text">Note Summary</span></div>
      <ul class="sidebar-nav">
        <li>
          <router-link to="/" exact-active-class="router-link-active">
            <span>✏️</span><span class="nav-text"> 记录</span>
          </router-link>
        </li>
        <li>
          <router-link to="/search" active-class="router-link-active">
            <span>🔍</span><span class="nav-text"> 搜索</span>
          </router-link>
        </li>
        <li>
          <router-link to="/categories" active-class="router-link-active">
            <span>📁</span><span class="nav-text"> 分类</span>
          </router-link>
        </li>
      </ul>
    </aside>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>
