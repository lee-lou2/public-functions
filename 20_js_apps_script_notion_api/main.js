function sha256(input) {
  var rawHash = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, input);
  var txtHash = '';
  for (var i = 0; i < rawHash.length; i++) {
    var hashVal = rawHash[i];
    if (hashVal < 0) {
      hashVal += 256;
    }
    if (hashVal.toString(16).length == 1) {
      txtHash += "0";
    }
    txtHash += hashVal.toString(16);
  }
  return txtHash;
}
function fetchRSSData() {
  var url = "";
  var response = UrlFetchApp.fetch(url);
  var data = response.getContentText();
  var document = XmlService.parse(data);
  var root = document.getRootElement();
  var entries = root.getChild("channel").getChildren("item");

  var rssData = [];
  for (var i = 0; i < entries.length; i++) {
    var entry = entries[i];
    var title = entry.getChild("title").getText();
    var link = entry.getChild("link").getText();
    var guid = entry.getChild("guid").getText();
    var categories = entry.getChildren("category");

    var tags = [];
    for (var j = 1; j < categories.length; j++) {
      tags.push(categories[j].getText());
    }

    var contentId = sha256(guid);

    rssData.push([title, link, tags.join(","), contentId]);
  }

  return rssData;
}

function getExistingContentIds(sheetId) {
  var sheet = SpreadsheetApp.openById(sheetId).getActiveSheet();
  var lastRow = sheet.getLastRow();
  var lastColumn = sheet.getLastColumn();

  if (lastRow <= 1 || lastColumn === 0) {
    return [];
  }

  var contentIdRange = sheet.getRange(2, lastColumn, lastRow - 1, 1);
  var contentIdValues = contentIdRange.getValues();

  var contentIds = [];
  for (var i = 0; i < contentIdValues.length; i++) {
    if (contentIdValues[i][0] !== "") {
      contentIds.push(contentIdValues[i][0]);
    }
  }

  return contentIds;
}

function filterNewData(data, existingContentIds) {
  var newData = [];

  for (var i = data.length - 1; i >= 0; i--) {
    var contentId = data[i][3];

    if (existingContentIds.indexOf(contentId) === -1) {
      newData.unshift(data[i]);
    }
  }

  return newData;
}

function saveToSheet(sheetId, data) {
  var sheet = SpreadsheetApp.openById(sheetId).getActiveSheet();
  var lastRow = sheet.getLastRow();

  if (lastRow === 0) {
    var headers = [["Title", "Link", "Tags", "contentId"]];
    sheet.getRange(1, 1, headers.length, headers[0].length).setValues(headers);
    sheet.getRange(lastRow + 2, 1, data.length, data[0].length).setValues(data);
  } else {
    var headerRange = sheet.getRange(1, 1, 1, sheet.getLastColumn());
    var headerValues = headerRange.getValues()[0];

    if (headerValues.join() !== headers[0].join()) {
      sheet.insertRowBefore(1);
      sheet.getRange(1, 1, headers.length, headers[0].length).setValues(headers);
    }
    sheet.getRange(lastRow + 1, 1, data.length, data[0].length).setValues(data);
  }
}

function addToNotion(data) {
  var notionToken = "";
  var databaseId = "";

  var headers = {
    "Authorization": "Bearer " + notionToken,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
  };

  for (var i = 0; i < data.length; i++) {
    var title = data[i][0];
    var link = data[i][1];
    var tags = data[i][2].split(",");

    var payload = {
      "parent": {
        "database_id": databaseId
      },
      "icon": {
          "type": "external",
          "external": {
              "url": "https://www.notion.so/icons/promoted_gray.svg"
          }
      },
      "properties": {
        "이름": {
          "title": [
            {
              "text": {
                "content": title
              }
            }
          ]
        },
        "URL": {
          "url": link
        },
        "태그": {
          "multi_select": tags.map(function(tag) {
            return {
              "name": tag
            };
          })
        }
      },
      "children": [
        {
          "object": "block",
          "type": "paragraph",
          "paragraph": {
            "rich_text": [
              {
                "type": "text",
                "text": {
                  "content": "본문 내용은 "
                }
              },
              {
                "type": "text",
                "text": {
                  "content": "여기",
                  "link": {
                    "url": link
                  }
                },
                "annotations": {
                  "bold": false,
                  "italic": false,
                  "strikethrough": false,
                  "underline": false,
                  "code": false,
                  "color": "default"
                }
              },
              {
                "type": "text",
                "text": {
                  "content": "에서 확인할 수 있습니다."
                }
              }
            ]
          }
        }
      ]
    };

    var options = {
      "method": "post",
      "headers": headers,
      "payload": JSON.stringify(payload)
    };

    UrlFetchApp.fetch("https://api.notion.com/v1/pages", options);
  }
}

function main() {
  var sheetId = "";

  var rssData = fetchRSSData();
  var existingContentIds = getExistingContentIds(sheetId);
  var newData = filterNewData(rssData, existingContentIds);

  if (newData.length > 0) {
    saveToSheet(sheetId, newData);
    addToNotion(newData);
  }
}
