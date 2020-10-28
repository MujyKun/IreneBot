export const successCode = 0;

export default function response(body) {
  let result;
  if (Object.prototype.hasOwnProperty.call(body, 'message')) {
    result = {
      code: successCode,
      text: body.message.result.translatedText,
      source: body.message.result.srcLangType,
    };
  } else {
    result = {
      code: body.errorCode,
      text: body.errorMessage,
      source: '',
    };
  }
  return result;
}
