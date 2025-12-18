// AWS Route Table actions

async function addRoute(event) {
  event.preventDefault();

  const rtbId = document.getElementById("rtbId").value;
  const destination = document.getElementById("destinationCidr").value;
  const targetType = document.getElementById("targetType").value;
  const targetId = document.getElementById("targetId").value;

  const url =
    `/api/v1/aws/route-tables/${rtbId}/routes` +
    `?destination_cidr=${destination}` +
    `&target_type=${targetType}` +
    `&target_id=${targetId}`;

  const res = await fetch(url, { method: "POST" });
  const data = await res.json();

  console.table(data);
  alert(data.status === "success" ? "Route added successfully" : data.error);
}
