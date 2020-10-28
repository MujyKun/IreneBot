import { assert } from 'chai';
import Translator from '../lib';

describe('Translator Class Tests', () => {
  let translator = {};
  before(() => {
    const clientId = process.env.CLIENT_ID || '';
    const clientSecret = process.env.CLIENT_SECRET || '';
    if (!clientId || !clientSecret) {
      throw new Error('You have to configure env.json');
    }
    translator = new Translator(clientId, clientSecret);
  });
  it('translate', (done) => {
    translator.translate('안녕하세요')
      .then((result) => {
        assert.equal(result.text, 'Hello.');
        done();
      })
      .catch((error) => {
        done(error);
      });
  });
  it('translate with source', (done) => {
    translator.translate('안녕하세요', 'ko', 'es')
      .then((result) => {
        assert.equal(result.text, 'Hola');
        done();
      })
      .catch((error) => {
        done(error);
      });
  });
  it('translate with invalid source', (done) => {
    translator.translate('안녕하세요', 'ko', 'da')
      .then((result) => {
        assert.equal(result.text, 'Hola');
        done();
      })
      .catch((error) => {
        assert.equal(error, 'Error: This languages is not supported');
        done();
      });
  });
  it('translate with failed status', (done) => {
    translator = new Translator('', '');
    translator.translate('안녕하세요')
      .then((result) => {
        assert.equal(result.text, 'Hello.');
        done();
      })
      .catch((error) => {
        assert.equal(error.code, '024');
        done();
      });
  });
});
