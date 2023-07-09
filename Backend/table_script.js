    fetch('/Backend/positions.json')
          .then(response => response.json())
          .then(data => {
            const tableContainer = document.getElementById('positions-table');
            const table = document.createElement('table');
            const tableHeader = document.createElement('thead');
            const headerRow = document.createElement('tr');
            const tickerHeader = document.createElement('th');
            tickerHeader.textContent = 'Ticker Symbol of Open Position';
            const profitLossHeader = document.createElement('th');
            profitLossHeader.textContent = 'Profit/Loss';
            const qtyHeader = document.createElement('th');
            qtyHeader.textContent = 'Quantity (Negative indicates a Short Position)';

            headerRow.appendChild(tickerHeader);
            headerRow.appendChild(profitLossHeader);
            headerRow.appendChild(qtyHeader);
            tableHeader.appendChild(headerRow);
            table.appendChild(tableHeader);
          const tableBody = document.createElement('tbody');
            data.forEach(item=>{
              const row = document.createElement('tr');
              const tickercell = document.createElement('td')
              tickercell.textContent = item.Symbol
              const profitLossCell = document.createElement('td');
              profitLossCell.textContent = item['Profit/Loss on Position'];
              const qtyCell = document.createElement('td');
              qtyCell.textContent = item['Quantity'];
              
              row.appendChild(tickercell);
              row.appendChild(profitLossCell);
              row.appendChild(qtyCell);
              tableBody.appendChild(row);
            });
          table.appendChild(tableBody);
          tableContainer.appendChild(table);
        })
        .catch(error => {
          console.error('Error:', error)
        });
    fetch('/Backend/output.json')
        .then(response => response.json())
        .then(data =>{
          const tableContainer = document.getElementById('signals-table');
          const table = document.createElement('table');
          const tableHeader = document.createElement('thead');
          const headerRow = document.createElement('tr');
          const signalHeader = document.createElement('th');
          signalHeader.textContent = 'Model Outputs';
          const timeHeader = document.createElement('th');
          timeHeader.textContent = 'Time';
          
          headerRow.appendChild(signalHeader);
          headerRow.appendChild(timeHeader);
          tableHeader.appendChild(headerRow);
          table.appendChild(tableHeader);
        const tableBody = document.createElement('tbody');
        data.forEach(item => {
          const row = document.createElement('tr');
          const signalCell = document.createElement('td');
          signalCell.textContent = item.Action;
          const timeCell = document.createElement('td');
          timeCell.textContent = item.Time;

          row.appendChild(signalCell);
          row.append(timeCell);
          tableBody.appendChild(row);
          });
        table.appendChild(tableBody);
        tableContainer.appendChild(table);
        })
        .catch(error => {
          console.error('Error:', error)
        });
    fetch('/Backend/portfolio_history.json')
        .then(response => response.json())
        .then(data => {
          const dates = data.map(entry => entry.date);
          const profitLoss = data.map(entry => entry.profit_loss);
          const equity = data.map(entry => entry.equity);
          console.log(data)
          const ctxProfit = document.getElementById('profitChart').getContext('2d');
          new Chart(ctxProfit, {
            type: 'line',
            data: {
              labels: dates,
              datasets: [
                {
                  label: 'Profit/Loss',
                  data: profitLoss,
                  backgroundColor: 'rgba(54, 162, 235, 0.2)',
                  borderColor: 'rgba(54, 162, 235, 1)',
                  borderWidth: 1
                }
              ]
            },
            options: {
              responsive: true,
              scales: {
                x: {
                  display: true,
                  title: {
                    display: true,
                    text: 'Date'
                  }
                },
                y: {
                  display: true,
                  title: {
                    display: true,
                    text: 'Profit/Loss ($)'
                  }
                }
              }
            }
          });
          const ctxEquity = document.getElementById('equityChart').getContext('2d')
          new Chart(ctxEquity, {
              type: 'line',
              data: {
                  labels: dates,
                  datasets: [
                      {
                          label: 'Equity',
                          data: equity,
                          backgroundColor: 'rgba(54, 162, 235, 0.2)',
                          borderColor: 'rgba(54, 162, 235, 1)',
                          borderWidth: 1
                      }
                  ]
              },
              options: {
                  responsive: true,
                  scales: {
                      x: {
                          display: true,
                          title: {
                              display: true, 
                              text: 'Date'
                          }
                      },
                      y: {
                          display: true,
                          title: {
                              display: true,
                              text: 'Equity'
                          }
                      }
                  }
              }
          });
        })
        .catch(error => {
            console.error('Error:', error);
        });
      
