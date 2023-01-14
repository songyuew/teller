const mongoose = require('mongoose');

const tokenSchema = new mongoose.Schema(
    {
        token: {
            type: String,
            required: [true, "A teller token must be provided"],
            unique: true,
            trim: true,
        },

        timestamp: {
            type: String,
            required: [true, "An entry must be timestamped"],
            trim: true
        }
    },
)

tokenSchema.post('save', function(doc, next) {
  console.log(doc);
  next();
});

const Token = mongoose.model('Token', tokenSchema);

module.exports = Token;