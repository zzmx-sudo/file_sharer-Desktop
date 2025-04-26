// 本地缓存服务
const PREFIX = "fileSharer_"

// 浏览历史模块
const BROWSE_PREFIX = `${PREFIX}browse_`
const BROWSE_PARAMS = `${BROWSE_PREFIX}params`
const BROWSE_HISTORY = `${BROWSE_PREFIX}history`

// 下载模块
const DOWNLOAD_PREFIX = `${PREFIX}download_`
const DOWNLOAD_HISTORY = `${DOWNLOAD_PREFIX}history`

// 上传模块
const UPLOAD_PREFIX = `${PREFIX}upload_`
const UPLOAD_HISTORY = `${UPLOAD_PREFIX}history`

const set = (key, data) => {
  localStorage.setItem(key, data);
}

const get = (key) => {
  return localStorage.getItem(key);
}

const remove = (key) => {
  localStorage.removeItem(key);
}

const clear = () => {
  localStorage.clear()
}

export default {
  set,
  get,
  remove,
  clear,
  BROWSE_PARAMS,
  BROWSE_HISTORY,
  DOWNLOAD_HISTORY,
  UPLOAD_HISTORY
}
