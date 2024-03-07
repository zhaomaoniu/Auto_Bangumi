export const useLogStore = defineStore('log', () => {
  const message = useMessage();
  const { isLoggedIn } = useAuth();
  const { t } = useMyI18n();

  const log = ref('');

  function get() {
    if (isLoggedIn.value) {
      apiLog.getLog().then((res) => {
        log.value = res;
      });
    }
  }

  const { execute: reset } = useApi(apiLog.clearLog, {
    showMessage: true,
    onSuccess() {
      log.value = '';
    },
  });

  const { pause: offUpdate, resume: onUpdate } = useIntervalFn(get, 3000, {
    immediate: false,
    immediateCallback: true,
  });

  function copy() {
    const { copy: copyLog, isSupported } = useClipboard({ source: log });
    if (isSupported) {
      copyLog();
      message.success(t('notify.copy_success'));
    } else {
      message.error(t('notify.copy_failed'));
    }
  }

  return {
    log,
    get,
    reset,
    onUpdate,
    offUpdate,
    copy,
  };
});
