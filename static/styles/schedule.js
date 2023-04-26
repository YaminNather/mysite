// Get all the table cells
const cells = document.querySelectorAll("table td");

// Loop through each cell
cells.forEach((cell) => {
  // Get the cell content
  const content = cell.textContent;

  // Clear the cell content
  cell.innerHTML = "";

  // Create a link with the original content as the link text
  const link = document.createElement("a");
  link.textContent = content;
  link.href = "#";

  // Create an input field with the original content as the initial value
  const input = document.createElement("input");
  input.type = "text";
  input.value = content;
  input.style.display = "none";

  // Add an event listener to the link that shows the input field
  link.addEventListener("click", (event) => {
    event.preventDefault();
    link.style.display = "none";
    input.style.display = "inline-block";
    input.focus();
  });

  // Add an event listener to the input field that saves the new value and updates the table
  input.addEventListener("blur", () => {
    link.textContent = input.value;
    link.style.display = "inline-block";
    input.style.display = "none";
    // Update the table with the new value
    const row = cell.parentNode;
    const rowData = [];
    const cells = row.querySelectorAll("td");
    cells.forEach((cell) => {
      rowData.push(cell.textContent);
    });
    // You can send an AJAX request to update the data in the database
    console.log("Updated row data:", rowData);
  });

  // Append the link and input field to the cell
  cell.appendChild(link);
  cell.appendChild(input);
});
