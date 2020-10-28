import rp from 'request-promise';
import { papagoApiUrl, contentType, languages } from './constants';
import response from './response';

export default class Translator {
  constructor(clientId, clientSecret) {
    this.clientId = clientId;
    this.clientSecret = clientSecret;
  }
  translate(text, _source, _target) {
    const source = _source || 'ko';
    const target = _target || 'en';
    return new Promise((resolve, reject) => {
      if (!Object.prototype.hasOwnProperty.call(languages, source) || !Object
        .prototype.hasOwnProperty.call(languages, target)) {
        reject(new Error('This languages is not supported'));
      }
      const options = {
        method: 'POST',
        uri: papagoApiUrl,
        form: {
          text,
          source,
          target,
        },
        headers: {
          'X-Naver-Client-Id': this.clientId,
          'X-Naver-Client-Secret': this.clientSecret,
          'Content-Type': contentType,
        },
        json: true,
      };
      rp(options)
        .then((body) => {
          const result = response(body);
          resolve(result);
        })
        .catch((err) => {
          const result = response(err.error);
          reject(result);
        });
    });
  }
}
