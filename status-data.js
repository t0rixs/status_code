// ステータスコード定義（サーバーなしでも動作）
const STATUS_DATABASE = {
  '100': { status: 100, phrase: 'Continue', description: 'Continue - リクエストの送信を続けてかまいません' },
  '101': { status: 101, phrase: 'Switching Protocols', description: 'Switching Protocols - プロトコルを切り替えます' },
  '102': { status: 102, phrase: 'Processing', description: 'Processing - サーバーは処理を続けています' },
  '103': { status: 103, phrase: 'Early Hints', description: 'Early Hints - 最終レスポンス前のヒントを返します' },
  '200': { status: 200, phrase: 'OK', description: 'OK - リクエストは成功しました' },
  '201': { status: 201, phrase: 'Created', description: 'Created - リソースが作成されました' },
  '204': { status: 204, phrase: 'No Content', description: 'No Content - 成功しましたが内容はありません' },
  '206': { status: 206, phrase: 'Partial Content', description: 'Partial Content - 部分的な内容を返します' },
  '300': { status: 300, phrase: 'Multiple Choices', description: 'Multiple Choices - 複数の選択肢があります' },
  '301': { status: 301, phrase: 'Moved Permanently', description: 'Moved Permanently - 永遠に別の場所に移動しました' },
  '302': { status: 302, phrase: 'Found', description: 'Found - 一時的に別の場所にあります' },
  '303': { status: 303, phrase: 'See Other', description: 'See Other - 別のURLを見てください' },
  '304': { status: 304, phrase: 'Not Modified', description: 'Not Modified - 変更されていません' },
  '307': { status: 307, phrase: 'Temporary Redirect', description: 'Temporary Redirect - 一時的にリダイレクトします' },
  '308': { status: 308, phrase: 'Permanent Redirect', description: 'Permanent Redirect - 永久的にリダイレクトします' },
  '400': { status: 400, phrase: 'Bad Request', description: 'Bad Request - リクエストが不正です' },
  '401': { status: 401, phrase: 'Unauthorized', description: 'Unauthorized - 認証が必要です' },
  '403': { status: 403, phrase: 'Forbidden', description: 'Forbidden - アクセスが禁止されています' },
  '404': { status: 404, phrase: 'Not Found', description: 'Not Found - ページが見つかりません' },
  '405': { status: 405, phrase: 'Method Not Allowed', description: 'Method Not Allowed - メソッドが許可されていません' },
  '408': { status: 408, phrase: 'Request Timeout', description: 'Request Timeout - リクエストがタイムアウトしました' },
  '409': { status: 409, phrase: 'Conflict', description: 'Conflict - リクエストが競合しています' },
  '410': { status: 410, phrase: 'Gone', description: 'Gone - リソースは削除されました' },
  '418': { status: 418, phrase: "I'm a Teapot", description: "I'm a Teapot - 紅茶を淹れるティーポットです（ジョーク）" },
  '429': { status: 429, phrase: 'Too Many Requests', description: 'Too Many Requests - リクエストが多すぎます' },
  '500': { status: 500, phrase: 'Internal Server Error', description: 'Internal Server Error - サーバーエラーが発生しました' },
  '501': { status: 501, phrase: 'Not Implemented', description: 'Not Implemented - 実装されていません' },
  '502': { status: 502, phrase: 'Bad Gateway', description: 'Bad Gateway - 不正なゲートウェイです' },
  '503': { status: 503, phrase: 'Service Unavailable', description: 'Service Unavailable - サービスが利用できません' },
  '504': { status: 504, phrase: 'Gateway Timeout', description: 'Gateway Timeout - ゲートウェイがタイムアウトしました' },
};

const REASON_PHRASES = {
  402: 'Payment Required',
};

function httpStatusForCode(code) {
  if (STATUS_DATABASE[code]) return STATUS_DATABASE[code].status;
  const n = parseInt(code, 10);
  if (n >= 100 && n <= 599) return n;
  return 404;
}

function buildPayload(code) {
  const entry = STATUS_DATABASE[code];
  const status = httpStatusForCode(code);
  const phrase = entry?.phrase || REASON_PHRASES[status] || 'Unknown';
  const description = entry?.description || `${phrase} - HTTP ${status}`;
  return { code, status, phrase, description };
}
