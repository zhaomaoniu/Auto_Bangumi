<script lang="ts" setup>
definePage({
  name: 'Player',
});

const { bangumi } = storeToRefs(useBangumiStore());
const { media } = storeToRefs(useMediaStore());
const { getAll } = useBangumiStore();
const { getEpisodes } = useMediaStore();

const { isMobile } = useBreakpointQuery();

const currentView = ref<'bangumiList' | 'episodeList' | 'player'>('bangumiList');
const selectedBangumiId = ref<number | null>(null);
const selectedEpisodeLink = ref<string | null>(null);

onActivated(() => {
  getAll();
});

// 切换到选集界面
const selectBangumi = (bangumiId: number) => {
  selectedBangumiId.value = bangumiId;
  currentView.value = 'episodeList';
  getEpisodes(bangumiId);
};

// 切换到播放界面
const selectEpisode = (episodeLink: string) => {
  selectedEpisodeLink.value = episodeLink;
  currentView.value = 'player';
};

// 返回到上一级界面
const backToList = () => {
  if (currentView.value === 'player') {
    currentView.value = 'episodeList';
  } else if (currentView.value === 'episodeList') {
    currentView.value = 'bangumiList';
  }
};
</script>

<template>
  <div class="container mt-12 flex-grow overflow-auto">
    <!-- Bangumi 列表 -->
    <div v-if="currentView === 'bangumiList'" class="bangumi-list">
      <transition-group name="fade" tag="div" class="bangumi-container">
        <ab-player-bangumi-card 
          v-for="i in bangumi" 
          :key="i.id" 
          :bangumi="i" 
          type="primary"
          @click="() => selectBangumi(i.id)"
          class="bangumi-card"
        />
      </transition-group>
    </div>

    <!-- 选集界面 -->
    <div v-if="currentView === 'episodeList' && selectedBangumiId !== null" class="episode-list">
      <div class="header">
        <button 
          @click="backToList"
          class="back-button">
          返回
        </button>
        <h2>选集</h2>
      </div>
      <transition-group name="fade" tag="div" class="episode-list-container">
        <div 
          v-for="episode in media[selectedBangumiId]" 
          :key="episode.link"
          class="episode-item"
          @click="() => selectEpisode(episode.link)"
        >
          {{ episode.title }}
        </div>
      </transition-group>
    </div>

    <!-- 播放界面 -->
    <div v-if="currentView === 'player' && selectedEpisodeLink !== null" class="player-view">
      <div class="header">
        <button 
          @click="backToList"
          class="back-button">
          返回
        </button>
        <h2>播放</h2>
      </div>
      <div class="video-container">
        <iframe 
          :src="selectedEpisodeLink" 
          frameborder="0" 
          title="video player"
          allowfullscreen
          class="video-player">
        </iframe>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 16px;
  text-align: left;
  max-width: none;
  background-color: rgb(240, 240, 240);
}

.header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  text-align: left;
}

.back-button {
  background: #492897; /* 按钮背景色 */
  color: #fff;
  border: none;
  padding: 6px 12px;
  font-size: 14px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.back-button:hover {
  background: rgb(40, 30, 82); /* 按钮悬停背景色 */
}

.bangumi-list {
  width: 100%;
  text-align: left;
}

.bangumi-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: flex-start;
  text-align: left;
}

.bangumi-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.bangumi-card:hover {
  transform: scale(1.05);
}

.episode-list {
  padding: 10px;
  width: 100%;
  text-align: left;
}

.episode-list-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: flex-start;
}

.episode-item {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 150px;
  height: 85px;
  background: #f3f3f3; /* 背景颜色 */
  border: 1px solid #ba68c8; /* 边框颜色 */
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.3s, background-color 0.3s;
  text-align: center;
}

.episode-item:hover {
  transform: scale(1.05);
  background-color: #f3e5f5; /* 悬停背景色 */
  color: #7b1fa2;
}

.player-view {
  width: 100%;
  padding: 10px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.video-container {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 长宽比 */
  text-align: left;
}

.video-player {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>
