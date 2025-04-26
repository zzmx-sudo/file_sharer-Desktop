import request from "./request";

export async function UploadChunk(
  uuid, secret_key, pwd, chunk, file_name,
  chunk_id, curr_path, hit_log=false
) {
  const url = !hit_log ? '/upload/' + uuid : '/upload/' + uuid + "?hit_log=true"
  const formData = new FormData();
  formData.append("secret_key", secret_key);
  formData.append("ciphertext", pwd);
  formData.append("file", chunk);
  formData.append("file_name", file_name);
  formData.append("chunk_id", chunk_id);
  formData.append("curr_path", curr_path);
  const response = await request.post(
    url,
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' }
    }
  );
  if ( response.errno != 200 ) {
    return {succed: false, data: response.errmsg}
  }
  return {succed: true, data: response.errmsg}
}

export async function UploadMerge(
  uuid, secret_key, pwd, file_name, chunk_count, curr_path
) {
  const formData = new FormData();
  formData.append("secret_key", secret_key);
  formData.append("ciphertext", pwd);
  formData.append("file_name", file_name);
  formData.append("chunk_count", chunk_count);
  formData.append("curr_path", curr_path);
  const response = await request.post(
    '/upload/merge/' + uuid,
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' }
    }
  );
  if ( response.errno != 200 ) {
    return {succed: false, data: response.errmsg}
  }
  return {succed: true, data: response.errmsg}
}

export async function UploadRemove(
  uuid, secret_key, pwd, file_name, curr_path
) {
  const formData = new FormData();
  formData.append("secret_key", secret_key);
  formData.append("ciphertext", pwd);
  formData.append("file_name", file_name);
  formData.append("curr_path", curr_path);
  const response = await request.post(
    '/upload/remove/' + uuid,
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' }
    }
  );
  console.log(response);
  if ( response.errno != 200 ) {
    return {succed: false, data: response.errmsg}
  }
  return {succed: true, data: response.errmsg}
}
