let difftreeBackend = (
    (spec, socket, session) => {
        function backend() {}

        backend.id = spec["id"];
        backend.type = "DifftreeBackend";
        backend.query_counter = 0;

        backend.execute = (query, callback, ids=[]) => {
            let cnt = backend.query_counter++;
            let qid = backend.id + "-" + cnt.toString();
            socket.on("data#" + qid, ({ sql, data }) => {
                callback({ sql, data })
            });
            socket.emit("execute", {session, payload: {"query": {"backend": spec["id"], "binding": query, "ids": ids}, "qid": qid}});
        };

        backend.to_sql = (query, ids, callback) => {
          socket.on("preview", ({preview}) => callback({preview}));
          socket.emit("previewsql", {session, payload: {"query": {"backend": spec["id"], "binding": query, "ids": ids}}});
        };

        return backend;
    });

export function DifftreeBackend() {
    function backend() {}

    backend.create = (
        (spec, socket, session) => {
            return difftreeBackend(spec, socket, session);
        }
    );

    return backend;
}

