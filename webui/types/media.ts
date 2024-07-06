/**
 * @type `BasicRule` in backend/src/module/models/media.py
 */
export interface BasicEpisodeRule {
    title: string;
    link: string;
}


export const ruleTemplate: BasicEpisodeRule = {
    title: '',
    link: '',
};