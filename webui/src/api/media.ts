import type { BasicEpisodeRule } from '#/media';


export const apiMedia = {
    /**
     * 获取指定 bangumi 的 episode 列表
     * @param bangumiId  bangumi id
     * @returns 指定 bangumi 的 episode 列表
     */
    async getEpisodes(bangumiId: number) {
        const { data } = await axios.get<BasicEpisodeRule[]>(
            `api/v1/_media/get/${bangumiId}`
        );
        return data;
    }
}