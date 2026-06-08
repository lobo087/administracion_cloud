module.exports = {
  networks: {
    development: {
      host: "ganache",
      port: 8545,
      network_id: "1337",
    },
  },
  compilers: {
    solc: {
      version: "0.8.19",
    },
  },
};
