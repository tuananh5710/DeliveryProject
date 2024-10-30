# Delivery Project

Xây dựng ứng dụng quản lý và điều phối đơn hàng theo yêu cầu sau:

## Khách hàng

* Tạo đơn hàng theo mức độ ưu tiên (Giao ngay/ Ưu tiên giao trước/ Hàng phổ thông giao chậm) Hoặc lập lịch giao hàng định kỳ 
* Địa chỉ cần giao đến 
* Theo dõi đơn hàng 

## Người giao hàng

* Đợi đơn đơn hàng 
* Đơn hàng theo độ ưu tiên 
* Đơn hàng được lập lịch định kỳ 
=> Lưu ý: Người giao hàng chỉ nhận được đơn hàng trong khu vực mình quản lý dựa theo địa chỉ giao hàng
* Sau khi nhận được đơn hàng, chuyển trạng thái đơn hàng (bắt đầu giao, đang giao, đã hoàn thành)
=> Lưu ý: Các trạng thái đơn hàng phải lưu lịch lại lịch sử (Thời gian bắt đầu giao, đang giao, hoàn thành)

## Tiến trình lập lịch

* Tự động push đơn hàng cho người giao hàng khi tới lịch giao hàng định kỳ

## Installation
1. pip install -r requirements.txt
2. python -m uvicorn app.main:app --reload
3. Install Redis ( cmd : redis-server )
   ```cmd
   redis-server
   ```
    https://github.com/MicrosoftArchive/redis/releases