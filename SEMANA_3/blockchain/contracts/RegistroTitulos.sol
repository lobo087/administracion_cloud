// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

contract RegistroTitulos{
    struct Titulo{
        bytes32 codigoTituloHash;
        bytes32 documentoHash;
        address universidad;
        uint256 fechaRegistro;
        bool existe;
    }

    mapping (bytes32 => Titulo) private titulos;

    event TituloRegistrado(
        bytes32 indexed codigoTituloHash,
        bytes32 indexed documentoHash,
        address indexed universidad
    );

    function registrarTitulo(
        bytes32 codigoTituloHash,
        bytes32 documentoHash
    ) public {
        require(!titulos[codigoTituloHash].existe, "El titulo ya existe");

        titulos[codigoTituloHash] = Titulo({
            codigoTituloHash: codigoTituloHash,
            documentoHash: documentoHash,
            universidad: msg.sender,
            fechaRegistro: block.timestamp,
            existe: true
        });

        emit TituloRegistrado(codigoTituloHash, documentoHash, msg.sender);
    }

    function verificarTitulo(bytes32 codigoTituloHash, bytes32 documentoHash)public view returns(bool existe, bool documentoCoincide) {
        Titulo memory titulo = titulos[codigoTituloHash];

        existe = titulo.existe;
        documentoCoincide = titulo.documentoHash == documentoHash;
    }

    function obtenerTitulo(bytes32 codigoTituloHash) public view returns (bytes32, bytes32, address, uint256, bool) {
        Titulo memory titulo = titulos[codigoTituloHash];
        return(
            titulo.codigoTituloHash,
            titulo.documentoHash,
            titulo.universidad,
            titulo.fechaRegistro,
            titulo.existe
        );
    }
}