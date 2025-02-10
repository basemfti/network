
document.addEventListener("DOMContentLoaded", function () {
  let form = document.getElementById("postForm");

  form.addEventListener("submit", function (event) {
      let content = document.getElementById("postContent").value.trim();

      if (content === "") {
          alert("Post content cannot be empty.");
          event.preventDefault(); // Stop form submission
      }
  });
});