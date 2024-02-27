const express = require('express');
const router = express.Router();

const systemLogic = require('logic/system.js');
const configLogic = require('logic/config');
const bitcoindLogic = require('logic/bitcoind.js');
const safeHandler = require('utils/safeHandler');
const validateSettingsRequest = require('utils/validateSettingsRequest');

router.get('/bitcoin-p2p-connection-details', safeHandler(async(req, res) => {
  const connectionDetails = systemLogic.getBitcoinP2PConnectionDetails();

  return res.json(connectionDetails);
}));

router.get('/bitcoin-rpc-connection-details', safeHandler(async(req, res) => {
  const connectionDetails = systemLogic.getBitcoinRPCConnectionDetails();

  return res.json(connectionDetails);
}));

router.get('/bitcoin-config', safeHandler(async(req, res) => {
  const bitcoinConfig = await configLogic.getJsonStore();
  return res.json(bitcoinConfig);
}));

// updateJsonStore / generateUmbrelBitcoinConfig / generateBitcoinConfig are all called through these routes below so that even if user closes the browser prematurely, the backend will complete the update.

router.post('/update-bitcoin-config', safeHandler(async(req, res) => {
  // store old bitcoinConfig in memory to revert to in case of errors setting new config and restarting bitcoind
  const oldBitcoinConfig = await configLogic.getJsonStore();
  const newBitcoinConfig = req.body.bitcoinConfig;

  const validationErrors = validateSettingsRequest(newBitcoinConfig);
  if (validationErrors.length > 0) {
    return res.status(400).json({success: false, validationErrors});
  }
  
  try {
    await configLogic.applyCustomBitcoinConfig(newBitcoinConfig);
    await bitcoindLogic.stop();

    res.json({success: true});
    
  } catch (error) {
    // revert everything to old config values
    await configLogic.applyCustomBitcoinConfig(oldBitcoinConfig);

    res.json({success: false}); // show error to user in UI
  }
}));

router.post('/restore-default-bitcoin-config', safeHandler(async(req, res) => {
  // store old bitcoinConfig in memory to revert to in case of errors setting new config and restarting bitcoind
  const oldBitcoinConfig = await configLogic.getJsonStore();
  
  try {
    await configLogic.applyDefaultBitcoinConfig();
    await bitcoindLogic.stop();

    res.json({success: true});
    
  } catch (error) {
    // revert everything to old config values
    await configLogic.applyCustomBitcoinConfig(oldBitcoinConfig);

    res.json({success: false}); // show error to user in UI
  }
}));

module.exports = router;