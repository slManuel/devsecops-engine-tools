import * as assert from 'assert';

import * as vscode from 'vscode';
import * as sinon from 'sinon';
import { Docker } from 'docker-cli-js';
import * as myExtension from '../../extension';
import * as InitEngineCore from '../../application/InitEngineCore';
import { IacScanRequest } from '../../infraestructure/entryPoint/IacScanRequest';
import { IIacScanUseCase } from '../../domain/usecase/interfaces/IIacScanUseCase';

suite('Extension Test Suite', () => {
	// Clean up after tests
	suiteTeardown(() => {
	  vscode.window.showInformationMessage('All tests done!');
	});
  
	// Clean up after each test
	teardown(() => {
	  sinon.restore();
	});
	
	test('Sample test', () => {
	  assert.strictEqual(-1, [1, 2, 3].indexOf(5));
	  assert.strictEqual(-1, [1, 2, 3].indexOf(0));
	});
  });
