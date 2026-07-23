// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

contract RegistroTitulos {
    enum EstadoTitulo {
        NO_EXISTE,
        REGISTRADO,
        AVALADO,
        RECHAZADO,
        REVOCADO
    }

    struct Titulo {
        bytes32 codigoTituloHash;
        bytes32 documentoHash;
        bytes32 identificacionEstudianteHash;
        string universidadEmisora;
        string carrera;
        string tituloObtenido;
        address universidad;
        address ministerioValidador;
        EstadoTitulo estado;
        uint256 fechaRegistro;
        uint256 fechaAval;
        bool existe;
    }

    mapping(bytes32 => Titulo) private titulos;
    bytes32[] private codigosTitulos;

    event TituloRegistrado(
        bytes32 indexed codigoTituloHash,
        bytes32 indexed documentoHash,
        bytes32 indexed identificacionEstudianteHash,
        string universidadEmisora,
        string carrera,
        string tituloObtenido,
        address universidad
    );

    event TituloAvalado(
        bytes32 indexed codigoTituloHash,
        address indexed ministerioValidador
    );

    function registrarTitulo(
        bytes32 codigoTituloHash,
        bytes32 documentoHash,
        bytes32 identificacionEstudianteHash,
        string memory universidadEmisora,
        string memory carrera,
        string memory tituloObtenido
    ) public {
        require(!titulos[codigoTituloHash].existe, "El titulo ya existe");

        titulos[codigoTituloHash] = Titulo({
            codigoTituloHash: codigoTituloHash,
            documentoHash: documentoHash,
            identificacionEstudianteHash: identificacionEstudianteHash,
            universidadEmisora: universidadEmisora,
            carrera: carrera,
            tituloObtenido: tituloObtenido,
            universidad: msg.sender,
            ministerioValidador: address(0),
            estado: EstadoTitulo.REGISTRADO,
            fechaRegistro: block.timestamp,
            fechaAval: 0,
            existe: true
        });

        codigosTitulos.push(codigoTituloHash);

        emit TituloRegistrado(
            codigoTituloHash,
            documentoHash,
            identificacionEstudianteHash,
            universidadEmisora,
            carrera,
            tituloObtenido,
            msg.sender
        );
    }

    function avalarTitulo(bytes32 codigoTituloHash) public {
        Titulo storage titulo = titulos[codigoTituloHash];

        require(titulo.existe, "El titulo no existe");
        require(titulo.estado == EstadoTitulo.REGISTRADO, "El titulo no esta pendiente de aval");

        titulo.estado = EstadoTitulo.AVALADO;
        titulo.ministerioValidador = msg.sender;
        titulo.fechaAval = block.timestamp;

        emit TituloAvalado(codigoTituloHash, msg.sender);
    }

    function verificarTitulo(
        bytes32 codigoTituloHash,
        bytes32 documentoHash,
        bytes32 identificacionEstudianteHash
    ) public view returns (
        bool existe,
        bool documentoCoincide,
        bool identificacionCoincide,
        EstadoTitulo estado
    ) {
        Titulo memory titulo = titulos[codigoTituloHash];

        existe = titulo.existe;
        documentoCoincide = titulo.documentoHash == documentoHash;
        identificacionCoincide = titulo.identificacionEstudianteHash == identificacionEstudianteHash;
        estado = titulo.estado;
    }

    function obtenerTitulo(bytes32 codigoTituloHash) public view returns (Titulo memory) {
        return titulos[codigoTituloHash];
    }

    function listarCodigosTitulos() public view returns (bytes32[] memory) {
        return codigosTitulos;
    }

    function totalTitulos() public view returns (uint256) {
        return codigosTitulos.length;
    }
}
