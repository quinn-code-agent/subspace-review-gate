import http from 'node:http';

const [listenHost, listenPortText, upstreamPortText] = process.argv.slice(2);
const listenPort = Number(listenPortText);
const upstreamPort = Number(upstreamPortText);

if (!listenHost || !Number.isInteger(listenPort) || !Number.isInteger(upstreamPort)) {
  throw new Error('usage: node loopback-proxy.mjs <listen-host> <listen-port> <human-review-port>');
}

const server = http.createServer((clientReq, clientRes) => {
  const headers = { ...clientReq.headers, host: `127.0.0.1:${upstreamPort}` };
  delete headers.connection;
  const upstreamReq = http.request({ host: '127.0.0.1', port: upstreamPort, method: clientReq.method, path: clientReq.url, headers }, (upstreamRes) => {
    clientRes.writeHead(upstreamRes.statusCode ?? 502, upstreamRes.headers);
    upstreamRes.pipe(clientRes);
  });
  upstreamReq.on('error', (error) => {
    if (!clientRes.headersSent) clientRes.writeHead(502, { 'content-type': 'text/plain; charset=utf-8' });
    clientRes.end(`Human Review upstream unavailable: ${error.message}`);
  });
  clientReq.pipe(upstreamReq);
});

server.listen(listenPort, listenHost, () => {
  console.log(`Loopback Human Review proxy listening on http://${listenHost}:${listenPort}`);
});
