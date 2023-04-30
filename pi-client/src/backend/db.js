let dbBackend = (
    (spec, socket, session) => {
        function backend() {}

        backend.id = spec["id"];
        backend.type = "DBBackend";
        backend.query_counter = 0;

        backend.execute = (query, callback) => {
            let cnt = backend.query_counter++;
            let qid = backend.id + "-" + cnt.toString();
            socket.on("data#" + ioid, ({ sql, data }) => callback({ sql, data }));
            socket.emit("execute", {session, payload: { "query": {"backend": spec["id"], "query": query}, "qid": qid} });
        };

        return backend;
    });

export function DBBackend() {
    function backend() {}

    backend.create = (
        (spec, socket, session) => {
            return dbBackend(spec, socket, session);
        }
    );

    return backend;
}

