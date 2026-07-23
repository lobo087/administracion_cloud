// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

contract RegistroTitulos {
    address public ministerioPrincipal;

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

    struct UniversidadAutorizada {
        string nombre;
        bool autorizada;
        uint256 fechaAutorizacion;
        bool existe;
    }

    mapping(bytes32 => Titulo) private titulos;
    bytes32[] private codigosTitulos;

    mapping(address => UniversidadAutorizada) private universidades;
    address[] private direccionesUniversidades;

    event UniversidadAutorizadaEvento(
        address indexed universidad,
        string nombre,
        address indexed ministerio,
        uint256 fechaAutorizacion
    );

    event UniversidadRevocada(
        address indexed universidad,
        address indexed ministerio,
        uint256 fechaRevocacion
    );

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

    modifier soloMinisterio() {
        require(msg.sender == ministerioPrincipal, "Solo el Ministerio puede ejecutar esta accion");
        _;
    }

    modifier soloUniversidadAutorizada() {
        require(universidades[msg.sender].autorizada, "Universidad no autorizada");
        _;
    }

    constructor(address _ministerioPrincipal, address _universidadInicial, string memory _nombreUniversidadInicial) {
        require(_ministerioPrincipal != address(0), "Ministerio invalido");
        ministerioPrincipal = _ministerioPrincipal;

        if (_universidadInicial != address(0)) {
            _autorizarUniversidad(_universidadInicial, _nombreUniversidadInicial);
        }
    }

    function autorizarUniversidad(address universidad, string memory nombre) public soloMinisterio {
        _autorizarUniversidad(universidad, nombre);
    }

    function revocarUniversidad(address universidad) public soloMinisterio {
        require(universidades[universidad].existe, "Universidad no registrada");
        universidades[universidad].autorizada = false;
        emit UniversidadRevocada(universidad, msg.sender, block.timestamp);
    }

    function _autorizarUniversidad(address universidad, string memory nombre) private {
        require(universidad != address(0), "Universidad invalida");
        require(bytes(nombre).length > 0, "Nombre requerido");

        if (!universidades[universidad].existe) {
            direccionesUniversidades.push(universidad);
        }

        universidades[universidad] = UniversidadAutorizada({
            nombre: nombre,
            autorizada: true,
            fechaAutorizacion: block.timestamp,
            existe: true
        });

        emit UniversidadAutorizadaEvento(universidad, nombre, ministerioPrincipal, block.timestamp);
    }

    function registrarTitulo(
        bytes32 codigoTituloHash,
        bytes32 documentoHash,
        bytes32 identificacionEstudianteHash,
        string memory universidadEmisora,
        string memory carrera,
        string memory tituloObtenido
    ) public soloUniversidadAutorizada {
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

    function avalarTitulo(bytes32 codigoTituloHash) public soloMinisterio {
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

    function obtenerUniversidad(address universidad) public view returns (UniversidadAutorizada memory) {
        return universidades[universidad];
    }

    function esUniversidadAutorizada(address universidad) public view returns (bool) {
        return universidades[universidad].autorizada;
    }

    function listarUniversidades() public view returns (address[] memory) {
        return direccionesUniversidades;
    }

    function listarCodigosTitulos() public view returns (bytes32[] memory) {
        return codigosTitulos;
    }

    function totalTitulos() public view returns (uint256) {
        return codigosTitulos.length;
    }
}
