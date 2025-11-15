import request from "./request";

export function GetListMobile(uuid) {
  return request.get('/file_list/' + uuid)
}

export function PostListMobile(uuid, secret_key, pwd) {
  return request.post(
    '/file_list/' + uuid,
    {
      'secret_key': secret_key,
      'ciphertext': pwd
    }
  )
}

export async function GetDownloadSpeed() {
  const response = await request.get(
    '/speed-test/download',
    {
      headers: { 'Cache-Control': 'no-cache' }
    }
  );
  return {succed: true}
}

export async function PostUploadSpeed() {
  const buffer = new Uint8Array(1048576);
  buffer.fill(0);
  const blob = new Blob([buffer], {type: 'application/octet-stream'});
  const formData = new FormData();
  formData.append('file', blob, 'speed_test.bin');
  const response = await request.post(
    '/speed-test/upload',
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' }
    }
  );
  if (response.errno != 200 || response.data.received_size != 1048576) {
    return {succed: false, duration: 0}
  } else {
    return {succed: true, duration: response.data.duration}
  }
}
