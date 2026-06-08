// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract HolaUTPL {
    string public mensaje;

    event MensajeActualizado(string nuevoMensaje);

    constructor(string memory mensajeInicial) {
        mensaje = mensajeInicial;
    }

    function actualizarMensaje(string memory nuevoMensaje) public {
        mensaje = nuevoMensaje;
        emit MensajeActualizado(nuevoMensaje);
    }
}
