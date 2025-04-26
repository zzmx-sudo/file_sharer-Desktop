export function deepClone(obj) {
  if (typeof obj !== 'object' || obj === null) {
    return obj;
  }

  let copy;

  if (Array.isArray(obj)) {
    copy = [];
    for (let i = 0; i < obj.length; i++) {
      copy.push(deepClone(obj[i]));
    }
  } else {
    copy = {};
    for (let key in obj) {
      if (obj.hasOwnProperty(key)) {
        copy[key] = deepClone(obj[key]);
      }
    }
  }

  return copy;
}

export function copyHistoryRMChunks(download_history) {
  if ( download_history == null ) {
    return download_history;
  }
  let download_history_ = [];
  for ( let i = 0; i < download_history.length; i++ ) {
    let download_item = deepClone(download_history[i]);
    // 下载完成的保留下载进度, 未完成的将下载进度置空
    if ( download_item.merged ) {
      download_item.succed_chunks = new Array(download_item.chunk_count).fill(0);
    } else {
      download_item.succed_chunks = [];
    }
    download_history_.push(download_item);
  }
  return download_history_;
}

export function mergeChunks(chunks, file_name) {
  const blob = new Blob(chunks);
  const documentElem = document.createElement('a');
  const href = window.URL.createObjectURL(blob);
  documentElem.href = href;
  documentElem.download = file_name;
  document.body.appendChild(documentElem);
  documentElem.click(); // 点击下载
  document.body.removeChild(documentElem); // 下载完成移除元素
  window.URL.revokeObjectURL(href); // 释放掉bl
}

export function copyHistoryRMFile(upload_history) {
  if ( upload_history == null ) {
    return upload_history;
  }
  let upload_history_ = [];
  for ( let i = 0; i < upload_history.length; i++ ) {
    let upload_item = deepClone(upload_history[i]);
    upload_item.file = null;
    upload_history_.push(upload_item);
  }
  return upload_history_;
}
