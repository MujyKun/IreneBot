'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _requestPromise = require('request-promise');

var _requestPromise2 = _interopRequireDefault(_requestPromise);

var _constants = require('./constants');

var _response = require('./response');

var _response2 = _interopRequireDefault(_response);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var Translator = function () {
  function Translator(clientId, clientSecret) {
    _classCallCheck(this, Translator);

    this.clientId = clientId;
    this.clientSecret = clientSecret;
  }

  _createClass(Translator, [{
    key: 'translate',
    value: function translate(text, _source, _target) {
      var _this = this;

      var source = _source || 'ko';
      var target = _target || 'en';
      return new Promise(function (resolve, reject) {
        if (!Object.prototype.hasOwnProperty.call(_constants.languages, source) || !Object.prototype.hasOwnProperty.call(_constants.languages, target)) {
          reject(new Error('This languages is not supported'));
        }
        var options = {
          method: 'POST',
          uri: _constants.papagoApiUrl,
          form: {
            text: text,
            source: source,
            target: target
          },
          headers: {
            'X-Naver-Client-Id': _this.clientId,
            'X-Naver-Client-Secret': _this.clientSecret,
            'Content-Type': _constants.contentType
          },
          json: true
        };
        (0, _requestPromise2.default)(options).then(function (body) {
          var result = (0, _response2.default)(body);
          resolve(result);
        }).catch(function (err) {
          var result = (0, _response2.default)(err.error);
          reject(result);
        });
      });
    }
  }]);

  return Translator;
}();

exports.default = Translator;