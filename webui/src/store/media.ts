import type { BasicEpisodeRule } from '#/media';

export const useMediaStore = defineStore('media', () => {
    const media = ref<Record<number, BasicEpisodeRule[]>>({});

    async function getEpisodes(bangumiId: number) {
        const res = await apiMedia.getEpisodes(bangumiId);
        media.value[bangumiId] = res;
    }

    return {
        media,
        getEpisodes,
    };
});
