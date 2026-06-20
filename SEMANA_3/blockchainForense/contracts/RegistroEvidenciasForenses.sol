// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

contract RegistroEvidenciasForenses {
    struct Evidencia {
        bytes32 codigoEvidenciaHash;
        bytes32 evidenciaHash;
        bytes32 casoHash;
        address registrador;
        uint256 fechaRegistro;
        bool existe;
    }

    mapping(bytes32 => Evidencia) private evidencias;

    event EvidenciaRegistrada(
        bytes32 indexed codigoEvidenciaHash,
        bytes32 indexed evidenciaHash,
        bytes32 indexed casoHash,
        address registrador,
        uint256 fechaRegistro
    );

    function registrarEvidencia(
        bytes32 codigoEvidenciaHash,
        bytes32 evidenciaHash,
        bytes32 casoHash
    ) public {
        require(!evidencias[codigoEvidenciaHash].existe, "La evidencia ya existe");
        require(codigoEvidenciaHash != bytes32(0), "Codigo de evidencia invalido");
        require(evidenciaHash != bytes32(0), "Hash de evidencia invalido");
        require(casoHash != bytes32(0), "Hash de caso invalido");

        evidencias[codigoEvidenciaHash] = Evidencia({
            codigoEvidenciaHash: codigoEvidenciaHash,
            evidenciaHash: evidenciaHash,
            casoHash: casoHash,
            registrador: msg.sender,
            fechaRegistro: block.timestamp,
            existe: true
        });

        emit EvidenciaRegistrada(
            codigoEvidenciaHash,
            evidenciaHash,
            casoHash,
            msg.sender,
            block.timestamp
        );
    }

    function verificarEvidencia(
        bytes32 codigoEvidenciaHash,
        bytes32 evidenciaHash
    ) public view returns (bool existe, bool evidenciaCoincide) {
        Evidencia memory evidencia = evidencias[codigoEvidenciaHash];

        existe = evidencia.existe;
        evidenciaCoincide = evidencia.existe && evidencia.evidenciaHash == evidenciaHash;
    }

    function obtenerEvidencia(
        bytes32 codigoEvidenciaHash
    ) public view returns (bytes32, bytes32, bytes32, address, uint256, bool) {
        Evidencia memory evidencia = evidencias[codigoEvidenciaHash];

        return (
            evidencia.codigoEvidenciaHash,
            evidencia.evidenciaHash,
            evidencia.casoHash,
            evidencia.registrador,
            evidencia.fechaRegistro,
            evidencia.existe
        );
    }
}
