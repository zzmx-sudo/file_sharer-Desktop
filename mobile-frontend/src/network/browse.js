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
