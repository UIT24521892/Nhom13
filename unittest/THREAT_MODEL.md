# Threat model và security requirements cho `json_search()`

## 1. Phạm vi và bối cảnh

`json_search(key, input_object, role=None)` tìm các trường theo `key` trong dữ liệu JSON trả về từ API giám sát hạ tầng mạng. Dữ liệu mẫu nằm trong `test_data.py`; quy tắc truy cập nằm trong `policy.py`. Hàm được dùng bởi ba vai trò `admin`, `operator` và `viewer`.

Mô hình này giả định ứng dụng gọi hàm đã xác thực người dùng và cung cấp role đáng tin cậy. Nếu người dùng tự đặt được giá trị `role`, việc kiểm tra role bên trong hàm không đủ để bảo vệ dữ liệu.

## 2. Threat model theo STRIDE — Yêu cầu 3 (a)–(d)

### (a) Actor/role và mục đích

| Role | Mục đích sử dụng | Phạm vi của các trường được định nghĩa trong `policy.py` |
| --- | --- | --- |
| `admin` | Quản trị, chẩn đoán thiết bị và sự cố | `apiKey`, `managementIpAddress`, `issueSummary` |
| `operator` | Theo dõi, xử lý sự cố vận hành | `managementIpAddress`, `issueSummary` |
| `viewer` | Theo dõi thông tin sự cố | `issueSummary` |

### (b) Asset cần bảo vệ

| Asset trong dữ liệu mẫu | Lý do cần bảo vệ |
| --- | --- |
| `apiKey` | Chứa chuỗi xác thực liên quan SNMP; chỉ `admin` được xem. |
| `managementIpAddress` | Tiết lộ địa chỉ quản trị thiết bị; chỉ `admin` và `operator` được xem. |
| `issueSummary` | Thông tin tóm tắt sự cố; cả ba role được xem theo policy. |

`apiKey` và `managementIpAddress` nằm bên trong cấu trúc JSON lồng nhau, cụ thể dưới `deviceDetails`. Vì vậy, kết quả chứa nguyên một object cha cũng có thể làm lộ các trường này.

### (c) Trust boundary

Ranh giới tin cậy nằm giữa dữ liệu JSON nội bộ của API và kết quả trả về cho người gọi có role cụ thể. `json_search()` phải đối chiếu role với chính sách truy cập **trước khi trả dữ liệu**, kể cả khi một trường nhạy cảm nằm trong object/list được trả về như một phần của kết quả lớn hơn. Nguồn cung cấp role phải được xác thực ở tầng ứng dụng gọi hàm.

### (d) Threat và phân loại STRIDE

| ID | Kịch bản đe dọa | Nhóm STRIDE | Hậu quả |
| --- | --- | --- | --- |
| T1 | `viewer` tìm trực tiếp `apiKey` hoặc `managementIpAddress` và hàm trả lại giá trị. | **Information Disclosure** | Rò rỉ chuỗi xác thực hoặc địa chỉ quản trị. |
| T2 | `viewer` tìm `deviceDetails` và hàm trả nguyên object có chứa `apiKey` và `managementIpAddress`. | **Information Disclosure** | Vượt qua kiểm tra chỉ dựa trên tên key được tìm kiếm. |
| T3 | Người gọi tự khai role là `admin` nếu tầng ứng dụng không xác thực hoặc không ràng buộc role với danh tính. | **Spoofing**; có thể dẫn đến **Elevation of Privilege** | Người dùng nhận quyền xem dữ liệu của `admin`. |

## 3. Security requirements rút ra từ threat model

| ID | Yêu cầu có thể kiểm thử | Liên kết |
| --- | --- | --- |
| SR-01 | Chỉ trả giá trị `apiKey` cho role `admin`; các role khác, role thiếu hoặc không hợp lệ nhận `[]` khi tìm trực tiếp trường này. | T1; `policy.py` |
| SR-02 | Chỉ trả giá trị `managementIpAddress` cho role `admin` hoặc `operator`; các role khác, role thiếu hoặc không hợp lệ nhận `[]` khi tìm trực tiếp trường này. | T1; `policy.py` |
| SR-03 | Cho phép `admin`, `operator`, `viewer` tìm `issueSummary`; hàm trả về các kết quả phù hợp tìm được trong dữ liệu lồng nhau. | Chức năng hợp lệ; `policy.py` |
| SR-04 | Bất kể key tìm kiếm là gì, kết quả dành cho người gọi không được chứa trường được bảo vệ mà role đó không có quyền đọc; cần kiểm soát cả object/list cha. | T2 |
| SR-05 | Tầng ứng dụng phải xác thực người dùng và truyền role đã được xác minh vào `json_search()`; không tin giá trị role do người dùng tự khai. | T3 |

## 4. Ca kiểm thử tối thiểu suy ra từ yêu cầu

1. `json_search("apiKey", data, role="viewer") == []` (SR-01).
2. `json_search("managementIpAddress", data, role="viewer") == []` (SR-02).
3. `json_search("issueSummary", data, role="viewer")` trả danh sách không rỗng (SR-03).
4. Kiểm tra bổ sung: tìm `deviceDetails` với `viewer` và xác nhận kết quả không chứa `apiKey` hoặc `managementIpAddress` (SR-04).

Trong bước đầu phát triển thủ công, ghi nhận lỗi chức năng của mã mẫu trước; sau khi sửa lỗi đệ quy mới bổ sung tham số `role` và các security test tương ứng.
