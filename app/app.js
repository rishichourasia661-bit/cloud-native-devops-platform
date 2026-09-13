const express = require("express");
const tasksRouter = require("./src/routes/tasks");

const app = express();

app.use(express.json());

app.get("/health", (req, res) => {
  res.status(200).json({
    status: "UP",
    message: "Application is healthy"
  });
});

app.use("/api/tasks", tasksRouter);

module.exports = app;