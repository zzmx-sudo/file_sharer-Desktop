const CryptoJS = require("crypto-js");


export function encrypt(plaintext, salt) {
  // 对盐值进行转换
  salt = CryptoJS.enc.Base64.parse(salt);
  // 生成密钥
  const keySize = 256 / 32; // AES-256
  const iterations = 100000;
  const derivedKey = CryptoJS.PBKDF2('secret_key', salt, {
    keySize: keySize,
    iterations: iterations,
    hasher: CryptoJS.algo.SHA256,
  });

  // 生成随机 IV
  const iv = CryptoJS.lib.WordArray.random(128 / 8);

  // 加密数据
  const encrypted = CryptoJS.AES.encrypt(plaintext, derivedKey, {
    iv: iv,
    padding: CryptoJS.pad.Pkcs7,
    mode: CryptoJS.mode.CBC,
  });

  // 返回盐值、IV 和加密数据的组合（Base64 编码）
  return (
    CryptoJS.enc.Base64.stringify(salt) +
    "|" +
    CryptoJS.enc.Base64.stringify(iv) +
    "|" +
    encrypted.toString()
  );
}
