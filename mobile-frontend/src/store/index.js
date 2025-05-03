import Vue from 'vue'
import Vuex from 'vuex'

import serviceStorage from "./serviceStorage"
import { DownloadChunk } from "@/network/download"
import { UploadChunk, UploadMerge, UploadRemove } from "@/network/upload"
import { copyHistoryRMChunks, mergeChunks, copyHistoryRMFile } from "@/utils/public_func"

Vue.use(Vuex)

export default new Vuex.Store({
  strict: process.env.NODE_ENV !== "production",
  state: {
    browse_params: JSON.parse(serviceStorage.get(serviceStorage.BROWSE_PARAMS)),
    browse_history: JSON.parse(serviceStorage.get(serviceStorage.BROWSE_HISTORY)),
    download_history: JSON.parse(serviceStorage.get(serviceStorage.DOWNLOAD_HISTORY)),
    upload_history: JSON.parse(serviceStorage.get(serviceStorage.UPLOAD_HISTORY))
  },
  mutations: {
    SET_BROWSE_PARAMS(state, params) {
      state.browse_params = params;
      serviceStorage.set(serviceStorage.BROWSE_PARAMS, JSON.stringify(params));
    },
    SET_BROWSE_HISTORY(state, browse_history) {
      state.browse_history = browse_history;
      serviceStorage.set(serviceStorage.BROWSE_HISTORY, JSON.stringify(browse_history));
    },
    UPDATE_BROWSE_HISTORY(state, browse_data) {
      var browse_history = state.browse_history;
      if (browse_history == null) {
        browse_history = [browse_data];
      } else {
        const idx = browse_history.findIndex(obj => obj.uuid == browse_data.uuid);
        if (idx != -1) {
          browse_history.splice(idx, 1, browse_data);
        } else {
          browse_history.push(browse_data);
        }
      };
      state.browse_history = browse_history;
      serviceStorage.set(serviceStorage.BROWSE_HISTORY, JSON.stringify(browse_history));
    },
    REMOVE_BROWSE_HISTORY(state, uuid) {
      var browse_history = state.browse_history;
      if (browse_history == null) {
        return;
      };
      const idx = browse_history.findIndex(obj => obj.uuid == uuid);
      if (idx != -1) {
        browse_history.splice(idx, 1);
        state.browse_history = browse_history;
        serviceStorage.set(serviceStorage.BROWSE_HISTORY, JSON.stringify(browse_history));
      }
    },
    CLEAR_BROWSE_HISTORY(state) {
      state.browse_history = null;
      serviceStorage.remove(serviceStorage.BROWSE_HISTORY);
    },
    UPDATE_DOWNLOAD_HISTORY(state, download_data) {
      var download_history = state.download_history;
      if (download_history == null) {
        download_history = {};
      }
      Vue.set(download_history, download_data.uuid, download_data);
      state.download_history = download_history;
      var download_history_ = copyHistoryRMChunks(download_history);
      serviceStorage.set(serviceStorage.DOWNLOAD_HISTORY, JSON.stringify(download_history_));
    },
    UPDATE_DOWNLOAD_ITEM(state, params) {
      var download_history = state.download_history;
      if (download_history == null) {
        return;
      }
      const {uuid, data} = params;
      const download_item = download_history[uuid];
      if (download_item != undefined) {
        const new_item = {...download_item, ...data};
        Vue.set(download_history, uuid, new_item);
      };
      state.download_history = download_history;
      var download_history_ = copyHistoryRMChunks(download_history);
      serviceStorage.set(serviceStorage.DOWNLOAD_HISTORY, JSON.stringify(download_history_));
    },
    PAUSE_DOWNLOAD_ITEM(state, uuid) {
      var download_history = state.download_history;
      if (download_history == null) {
        return;
      };
      const download_item = download_history[uuid];
      if (download_item != undefined) {
        download_item.is_pause = true;
        state.download_history = download_history;
        var download_history_ = copyHistoryRMChunks(download_history);
        serviceStorage.set(serviceStorage.DOWNLOAD_HISTORY, JSON.stringify(download_history_));
      }
    },
    REMOVE_DOWNLOAD_ITEM(state, uuid) {
      var download_history = state.download_history;
      if (download_history == null) {
        return;
      };
      const download_item = download_history[uuid];
      if (download_item != undefined) {
        Vue.delete(download_history, uuid);
        state.download_history = download_history;
        var download_history_ = copyHistoryRMChunks(download_history);
        serviceStorage.set(serviceStorage.DOWNLOAD_HISTORY, JSON.stringify(download_history_));
      }
    },
    PAUSE_ALL_DOWNLOAD_HISTORY(state) {
      var download_history = state.download_history;
      if (download_history == null) {
        return;
      };
      Object.values(download_history).forEach(download_item => {
        download_item.is_pause = true;
      });
      state.download_history = download_history;
      var download_history_ = copyHistoryRMChunks(download_history);
      serviceStorage.set(serviceStorage.DOWNLOAD_HISTORY, JSON.stringify(download_history_));
    },
    CLEAR_DOWNLOAD_HISTORY(state) {
      state.download_history = null;
      serviceStorage.remove(serviceStorage.DOWNLOAD_HISTORY);
    },
    UPDATE_UPLOAD_HISTORY(state, upload_data) {
      var upload_history = state.upload_history;
      if (upload_history == null) {
        upload_history = {};
      }
      Vue.set(upload_history, upload_data.file_id, upload_data);
      state.upload_history = upload_history;
      var upload_history_ = copyHistoryRMFile(upload_history);
      serviceStorage.set(serviceStorage.UPLOAD_HISTORY, JSON.stringify(upload_history_));
    },
    UPDATE_UPLOAD_ITEM(state, params) {
      var upload_history = state.upload_history;
      if (upload_history == null) {
        return;
      }
      const {file_id, data} = params;
      const upload_item = upload_history[file_id];
      if (upload_item != undefined) {
        const new_item = {...upload_item, ...data};
        Vue.set(upload_history, file_id, new_item);
      }
      state.upload_history = upload_history;
      var upload_history_ = copyHistoryRMFile(upload_history);
      serviceStorage.set(serviceStorage.UPLOAD_HISTORY, JSON.stringify(upload_history_));
    },
    PAUSE_UPLOAD_ITEM(state, file_id) {
      var upload_history = state.upload_history;
      if (upload_history == null) {
        return;
      };
      const upload_item = upload_history[file_id];
      if (upload_item != undefined) {
        upload_item.is_pause = true;
        state.upload_history = upload_history;
        var upload_history_ = copyHistoryRMFile(upload_history);
        serviceStorage.set(serviceStorage.UPLOAD_HISTORY, JSON.stringify(upload_history_));
      }
    },
    REMOVE_UPLOAD_ITEM(state, file_id) {
      var upload_history = state.upload_history;
      if (upload_history == null) {
        return;
      };
      const upload_item = upload_history[file_id];
      if (upload_item != undefined) {
        Vue.delete(upload_history, file_id);
        state.upload_history = upload_history;
        var upload_history_ = copyHistoryRMFile(upload_history);
        serviceStorage.set(serviceStorage.UPLOAD_HISTORY, JSON.stringify(upload_history_));
      }
    },
    PAUSE_ALL_UPLOAD_HISTORY(state) {
      var upload_history = state.upload_history;
      if (upload_history == null) {
        return;
      };
      Object.values(upload_history).forEach(upload_item => {
        upload_item.is_pause = true;
      });
      state.upload_history = upload_history;
      var upload_history_ = copyHistoryRMFile(upload_history);
      serviceStorage.set(serviceStorage.UPLOAD_HISTORY, JSON.stringify(upload_history_));
    },
    CLEAR_UPLOAD_HISTORY(state) {
      state.upload_history = null;
      serviceStorage.remove(serviceStorage.UPLOAD_HISTORY);
    }
  },
  actions: {
    async START_DOWNLOAD_FILE(context, uuid) {
      // 理应不会进这个判断
      var download_history = context.state.download_history;
      if ( download_history == null || download_history[uuid] == undefined ) {
        return
      }
      var download_item = download_history[uuid];
      context.commit("UPDATE_DOWNLOAD_ITEM", {uuid: uuid, data: {succed_chunks: []}});
      for (let i = 0; i < download_item.chunk_count; i++) {
        if ( context.state.download_history[uuid].is_pause ) {
          return;
        }
        const start = i * download_item.chunk_size;
        const end = Math.min(start + download_item.chunk_size, download_item.file_size);
        const res = await DownloadChunk(
          download_item.uuid, download_item.secret_key,
          download_item.pwd, start, end, i == 0
        );
        if ( !res.succed ) {
          context.commit("UPDATE_DOWNLOAD_ITEM", {uuid: uuid, data: {failed: true, err_msg: res.data}});
          return;
        }
        context.commit("UPDATE_DOWNLOAD_ITEM", {
          uuid: uuid,
          data: {
            succed_chunks: [...context.state.download_history[uuid].succed_chunks, res.data]
          }
        });
      };
      mergeChunks(context.state.download_history[uuid].succed_chunks, download_item.file_name);
      context.commit("UPDATE_DOWNLOAD_ITEM", {
        uuid: uuid, data: {merged: true, succed_chunks: new Array(download_item.chunk_count).fill(0)}
      });
    },
    async REDOWNLOAD_FILE(context, uuid) {
      // 理应不会进这个判断
      var download_history = context.state.download_history;
      if ( download_history == null || download_history[uuid] == undefined ) {
        return;
      }
      var download_item = download_history[uuid];
      context.commit("UPDATE_DOWNLOAD_ITEM", {uuid: uuid, data: {failed: false, err_msg: "", is_pause: false}});
      for (let i = download_item.succed_chunks.length; i < download_item.chunk_count; i++) {
        if ( context.state.download_history[uuid].is_pause ) {
          return;
        }
        const start = i * download_item.chunk_size;
        const end = Math.min(start + download_item.chunk_size, download_item.file_size);
        const res = await DownloadChunk(
          download_item.uuid, download_item.secret_key,
          download_item.pwd, start, end
        );
        if ( !res.succed ) {
          context.commit("UPDATE_DOWNLOAD_ITEM", {uuid: uuid, data: {failed: true, err_msg: res.data}});
          return;
        }
        context.commit("UPDATE_DOWNLOAD_ITEM", {
          uuid: uuid,
          data: {
            succed_chunks: [...context.state.download_history[uuid].succed_chunks, res.data]
          }
        });
      }
      mergeChunks(context.state.download_history[uuid].succed_chunks, download_item.file_name);
      context.commit("UPDATE_DOWNLOAD_ITEM", {
        uuid: uuid, data: {merged: true, succed_chunks: new Array(download_item.chunk_count).fill(0)}
      });
    },
    async START_UPLOAD_FILE(context, file_id) {
      // 理应不会进这个判断
      var upload_history = context.state.upload_history;
      if ( upload_history == null || upload_history[file_id] == undefined ) {
        return;
      }
      var upload_item = upload_history[file_id];
      if ( upload_item.file == null ) {
        context.commit("UPDATE_UPLOAD_ITEM", {file_id: file_id, data: {failed: true, err_msg: "选择的文件数据丢失"}});
        return;
      }
      context.commit("UPDATE_UPLOAD_ITEM", {file_id: file_id, data: {succed_chunks: [], failed: false}});
      for (let i = 0; i < upload_item.chunk_count; i++) {
        if ( context.state.upload_history[file_id].is_pause ) {
          return;
        }
        const start = i * upload_item.chunk_size;
        const end = Math.min(start + upload_item.chunk_size, upload_item.file_size);
        const chunk = upload_item.file.slice(start, end);
        const res = await UploadChunk(
          upload_item.uuid, upload_item.secret_key, upload_item.pwd, chunk,
          upload_item.file_name, i, upload_item.curr_path, i == 0
        );
        if ( !res.succed ) {
          context.commit("UPDATE_UPLOAD_ITEM", {file_id: file_id, data: {failed: true, err_msg: res.data}});
          return;
        }
        context.commit("UPDATE_UPLOAD_ITEM", {
          file_id: file_id,
          data: {
            succed_chunks: [...context.state.upload_history[file_id].succed_chunks, i]
          }
        });
      };
      const res = await UploadMerge(
        upload_item.uuid, upload_item.secret_key, upload_item.pwd,
        upload_item.file_name, upload_item.chunk_count, upload_item.curr_path
      )
      if ( !res.succed ){
        context.commit("UPDATE_UPLOAD_ITEM", {file_id: file_id, data: {failed: true, err_msg: res.data}});
        return;
      }
      context.commit("UPDATE_UPLOAD_ITEM", {file_id: file_id, data: {merged: true, file: null}});
    },
    async REUPLOAD_FILE(context, file_id) {
      var upload_history = context.state.upload_history;
      if ( upload_history == null || upload_history[file_id] == undefined ) {
        return;
      }
      var upload_item = upload_history[file_id];
      if ( upload_item.file == null ) {
        context.commit("UPDATE_UPLOAD_ITEM", {file_id: file_id, data: {failed: true, err_msg: "选择的文件数据丢失"}});
        return;
      }
      context.commit("UPDATE_UPLOAD_ITEM", {file_id: file_id, data: {failed: false, err_msg: "", is_pause: false}});
      for (let i = upload_item.succed_chunks.length; i < upload_item.chunk_count; i++) {
        if ( context.state.upload_history[file_id].is_pause ) {
          return;
        }
        const start = i * upload_item.chunk_size;
        const end = Math.min(start + upload_item.chunk_size, upload_item.file_size);
        const chunk = upload_item.file.slice(start, end);
        const res = await UploadChunk(
          upload_item.uuid, upload_item.secret_key, upload_item.pwd, chunk,
          upload_item.file_name, i, upload_item.curr_path, i == 0
        );
        if ( !res.succed ) {
          context.commit("UPDATE_UPLOAD_ITEM", {file_id: file_id, data: {failed: true, err_msg: res.data}});
          return;
        }
        context.commit("UPDATE_UPLOAD_ITEM", {
          file_id: file_id,
          data: {
            succed_chunks: [...context.state.upload_history[file_id].succed_chunks, i]
          }
        });
      };
      const res = await UploadMerge(
        upload_item.uuid, upload_item.secret_key, upload_item.pwd,
        upload_item.file_name, upload_item.chunk_count, upload_item.curr_path
      )
      if ( !res.succed ){
        context.commit("UPDATE_UPLOAD_ITEM", {file_id: file_id, data: {failed: true, err_msg: res.data}});
        return;
      }
      context.commit("UPDATE_UPLOAD_ITEM", {file_id: file_id, data: {merged: true, file: null}});
    },
    async REMOVE_UPLOAD_FILE(context, file_id) {
      var upload_history = context.state.upload_history;
      if ( upload_history == null || upload_history[file_id] == undefined ) {
        return;
      }
      var upload_item = upload_history[file_id];
      if ( !upload_item.merged && upload_item.succed_chunks.length != 0 ) {
        await UploadRemove(
          upload_item.uuid, upload_item.secret_key, upload_item.pwd,
          upload_item.file_name, upload_item.curr_path
        );
      }
      context.commit("REMOVE_UPLOAD_ITEM", upload_item.file_id);
    }
  },
  getters: {
    download_list: state => {
      return Object.values(state.download_history);
    },
    upload_list: state => {
      return Object.values(state.upload_history);
    }
  },
  modules: {}
})
