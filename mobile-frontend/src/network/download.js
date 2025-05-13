import request from "./request";

export function GetFileSize(uuid) {
  return request.get('/file_size/' + uuid)
}

export async function DownloadChunk(uuid, secret_key, pwd, start, end, hit_log=false) {
  const url = !hit_log ? '/download/' + uuid : '/download/' + uuid + "?hit_log=true";
  const response = await request.post(
    url,
    {
      'secret_key': secret_key,
      'ciphertext': pwd
    },
    {
      headers: { Range: `bytes=${start}-${end}` },
      responseType: 'blob',
    }
  );
  if ( response.errno != undefined ) {
    return {succed: false, data: response.errmsg}
  }
  if ( !response instanceof Blob) {
    return {succed: false, data: "后端异常, 返回非预期数据类型"}
  }
  const chunk_size = end - start;
  if ( chunk_size > 0 && chunk_size != response.size ) {
    return {succed: false, data: "下载片段失败, 服务器网络异常"}
  }
  return {succed: true, data: response}
}
