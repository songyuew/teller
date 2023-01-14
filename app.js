const express = require('express');
const morgan = require('morgan');
const controller = require("./controller")

const app = express();

if (process.env.NODE_ENV === 'development') {
  app.use(morgan('dev'));
}

app.use(express.json())

app.use(express.static("./public"));

app.use((req, res, next) => {
    req.body.timestamp = new Date().toISOString();
    next();
});

const router = express.Router();
router
  .route('/')
  .post(controller.postCredentials);

app.use('/api/v1', router);

module.exports = app;