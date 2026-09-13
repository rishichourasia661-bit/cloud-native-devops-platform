const express = require("express");

const router = express.Router();

let tasks = [
  {
    id: 1,
    title: "Learn Docker",
    completed: false
  },
  {
    id: 2,
    title: "Build Kubernetes deployment",
    completed: false
  }
];

router.get("/", (req, res) => {
  res.status(200).json(tasks);
});

router.get("/:id", (req, res) => {
  const id = Number(req.params.id);
  const task = tasks.find((task) => task.id === id);

  if (!task) {
    return res.status(404).json({
      error: "Task not found"
    });
  }

  res.status(200).json(task);
});

router.post("/", (req, res) => {
  const { title } = req.body;

  if (!title) {
    return res.status(400).json({
      error: "Title is required"
    });
  }

  const newTask = {
    id: tasks.length + 1,
    title,
    completed: false
  };

  tasks.push(newTask);

  res.status(201).json(newTask);
});

router.put("/:id", (req, res) => {
  const id = Number(req.params.id);
  const task = tasks.find((task) => task.id === id);

  if (!task) {
    return res.status(404).json({
      error: "Task not found"
    });
  }

  const { title, completed } = req.body;

  if (title !== undefined) {
    task.title = title;
  }

  if (completed !== undefined) {
    task.completed = completed;
  }

  res.status(200).json(task);
});

router.delete("/:id", (req, res) => {
  const id = Number(req.params.id);
  const taskIndex = tasks.findIndex((task) => task.id === id);

  if (taskIndex === -1) {
    return res.status(404).json({
      error: "Task not found"
    });
  }

  const deletedTask = tasks.splice(taskIndex, 1);

  res.status(200).json(deletedTask[0]);
});

module.exports = router;