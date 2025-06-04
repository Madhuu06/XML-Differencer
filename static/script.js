document.getElementById("compareBtn").addEventListener("click", function () {
  const xml1 = document.getElementById("text1").value.trim();
  const xml2 = document.getElementById("text2").value.trim();

  if (!xml1 || !xml2) {
    alert("Please paste XML into both text boxes.");
    return;
  }

  fetch("/api/compare", {  // <-- FIXED endpoint
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ xml1, xml2 })
  })
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        alert("Error: " + data.error);
        return;
      }

      const tbody = document.querySelector("#diffTable tbody");
      tbody.innerHTML = "";

      if (data.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="3" class="px-4 py-2 text-center text-green-600">No differences found</td>
          </tr>
        `;
        return;
      }

      data.forEach(diff => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td class="px-4 py-2">${diff["Attribute"] || "-"}</td>
          <td class="px-4 py-2">${diff["Tag Path"] || "-"}</td>
          <td class="px-4 py-2">${diff["Difference Type"] || "-"}</td>
        `;
        tbody.appendChild(row);
      });
    })
    .catch(error => {
      alert("Error occurred: " + error);
      console.error(error);
    });
});
