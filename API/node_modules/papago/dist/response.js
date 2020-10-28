'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = response;
var successCode = exports.successCode = 0;

function response(body) {
  var result = void 0;
  if (Object.prototype.hasOwnProperty.call(body, 'message')) {
    result = {
      code: successCode,
      text: body.message.result.translatedText,
      source: body.message.result.srcLangType
    };
  } else {
    result = {
      code: body.errorCode,
      text: body.errorMessage,
      source: ''
    };
  }
  return result;
}