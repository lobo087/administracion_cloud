# Vision general

Semana 6 simula una red academica distribuida en tres nubes.

```text
UTPL registra titulos.
Ministerio avala titulos.
Auditora Espana verifica titulos.
```

Cada actor opera su propia infraestructura:

```text
UTPL: API + PostgreSQL + Geth
Ministerio: API + PostgreSQL + Geth
Auditora: API + PostgreSQL + Geth
```

La blockchain es una capa compartida de verificacion. No guarda datos personales completos. Guarda hashes, estados y evidencia verificable.
