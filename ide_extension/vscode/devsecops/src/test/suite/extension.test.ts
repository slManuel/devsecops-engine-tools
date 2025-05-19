import * as assert from 'assert';

import * as vscode from 'vscode';
import * as sinon from 'sinon';

suite('Extension Test Suite', () => {
	// Clean up after tests
	suiteTeardown(() => {
	  void vscode.window.showInformationMessage('All tests done!');
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
