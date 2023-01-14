const Credentials = require("./tokenModel")

exports.postCredentials = async (req,res) => {
    try{
        const doc = await Credentials.create(req.body);
        res.status(201).json({
            status: 'success',
            data: {
                credentials: doc
            }
        })
    } catch (err) {
        res.status(400).json({
            status: 'fail',
            message: err
        })
    }
}