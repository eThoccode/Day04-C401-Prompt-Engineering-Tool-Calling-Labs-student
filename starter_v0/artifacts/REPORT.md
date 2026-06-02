# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, đã hoàn thiện đầy đủ cấu trúc và nội dung thực tế dựa trên kết quả tối ưu hóa:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn giới thiệu các tools, các tính năng và đường link trải nghiệm Web UI.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ log thật từ v0 đến v2, phân tích lỗi, danh sách 10 testcases của nhóm và bằng chứng chạy thực tế.

## Team

- **Team:** Team 5, Zone 4
- **Members:** Vũ Minh Duy, Phan Anh Thắng
- **Provider/model:** Gemini (Gemini 1.5 Flash / Gemini 3.5 Flash)

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent của nhóm 5 là một tác nhân nghiên cứu thông minh, có khả năng tra cứu thông tin/tin tức thời sự trên web, tìm kiếm các bài viết nổi bật trên Twitter (theo từ khóa hoặc theo tài khoản chuyên gia), truy cập bài báo khoa học học thuật arXiv, tóm tắt văn bản thông minh (tool mới `summarizer`), tự động xuất báo cáo Markdown ra file vật lý cục bộ trên đĩa (tool mới `exporter`), và đăng tin lên Telegram với cơ chế xác nhận an toàn tuyệt đối.

**Link dùng thử (deploy Web UI qua Cloudflare Tunnel):**  
🔗 [https://travesti-settings-extreme-ones.trycloudflare.com](https://travesti-settings-extreme-ones.trycloudflare.com)

---

## A2. Tool agent có

Hệ thống sở hữu bộ công cụ đa dạng hỗ trợ đắc lực cho các nghiệp vụ nghiên cứu và kiểm thử, trong đó có **2 công cụ mới** được nhóm tự thiết kế và tích hợp thêm:

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| **clarify** | Hỏi lại người dùng khi thiếu tham số cần thiết (handle, URL) hoặc xin ý kiến xác nhận Yes/No trước khi hành động. | Không |
| **timeline** | Lấy các bài đăng (tweets) gần đây nhất từ một tài khoản chỉ định. | Không |
| **social_search** | Tìm kiếm các bài viết nổi bật trên Twitter theo từ khóa mong muốn (sắp xếp Top/Latest). | Không |
| **lookup** | Tìm kiếm tin tức hoặc thông tin tổng hợp trên Internet với giới hạn thời gian (ngày, tuần, tháng, năm). | Không |
| **fetch** | Cào và đọc nội dung chi tiết dạng Markdown của một địa chỉ URL cụ thể. | Không |
| **format** | Định dạng các bài đăng thu thập được thành bản tin markdown digest theo các mẫu cấu trúc chuyên nghiệp. | Không |
| **send** | Gửi/Đăng tải bản tin lên Telegram channel (bắt buộc phải qua bước xác nhận đồng ý). | Không |
| **policy** | Tìm kiếm tài liệu, chính sách nội bộ của công ty. | Không |
| **papers** | Tra cứu các bài báo khoa học học thuật trên thư viện arXiv theo từ khóa. | Không |
| **paper_text** | Tải và trích xuất nội dung văn bản từ các trang của file PDF bài báo arXiv. | Không |
| **summarizer** | Tóm tắt đoạn văn bản dài thành dạng gạch đầu dòng (bullets) hoặc đoạn văn (paragraph) bằng thuật toán chấm điểm tần suất từ (extractive scoring). | **CÓ (Tool mới thêm)** |
| **exporter** | Tự động ghi và xuất nội dung báo cáo ra file vật lý dạng `.md` hoặc `.txt` trên thư mục đĩa cục bộ. | **CÓ (Tool mới thêm)** |

---

## A3. Câu hỏi mẫu để thử

Dưới đây là các câu hỏi mẫu cực kỳ hay để bạn trải nghiệm ngay trên giao diện Web UI:

1. **Tìm kiếm & Trích xuất:** *"Tin tức AI nổi bật nhất hôm nay là gì? Sau khi tìm được, hãy lấy nội dung của link bài báo đầu tiên."* (Agent sẽ tự động gọi `lookup` với `timeframe="day"`, sau đó chạy `fetch` để đọc URL).
2. **Hỏi lại khi thiếu thông tin:** *"Tóm tắt 5 tweet mới nhất giúp mình"* (Agent nhận ra thiếu tên tài khoản nên sẽ gọi `clarify` để hỏi lại bạn).
3. **Sử dụng Tool tóm tắt mới:** *"Tóm tắt đoạn văn bản sau dưới dạng gạch đầu dòng: OpenAI vừa ra mắt model siêu trí tuệ GPT-5..."* (Agent sẽ định tuyến chuẩn xác tới tool `summarizer`).
4. **Sử dụng Tool ghi file mới:** *"Lưu nội dung báo cáo nghiên cứu này ra file 'bao_cao_nghien_cuu.md': # Báo cáo công nghệ..."* (Agent sẽ gọi `exporter` để ghi file lên ổ cứng của bạn).
5. **Đăng Telegram có xác nhận an toàn:** *"Đăng bản tin AI ngày hôm nay lên kênh Telegram giúp mình nhé."* (Agent sẽ gọi `clarify` dạng `yes_no` để hỏi xác nhận của bạn trước khi thực hiện).

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Các chỉ số được ghi nhận chi tiết qua các phiên bản tối ưu hóa của nhóm:

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| **v0** | baseline prompt | Prompt mặc định mơ hồ, hướng dẫn đoán bừa và không xác nhận. | 0.00% | **71.43%** | `runs/v0_B_base_gemini_20260602T134709688106.json` |
| **v1** | `system_prompt.md` | Sử dụng cấu trúc các thẻ XML-like phân tách ranh giới và luật nghiêm ngặt. | 71.43% | **90.91%** | `runs/v1_B_base_gemini_20260602T140552328218.json` |
| **v2** | `system_prompt.md` + `tools.yaml` | Thêm quy tắc cấm nháy kép trong search query và dịch toàn bộ schema tools sang tiếng Anh. | 90.91% | **100.00%** | `runs/v1_B_base_gemini_20260602T141650149389.json` (best run) |

---

## B2. Failure Analysis

Phân tích các ca kiểm thử thất bại tiêu biểu ở Baseline v0 và biện pháp khắc phục ở bản v1 & v2:

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| **R03_web_news_routing** | wrong_arg_value | `lookup(query="AI news")` | Agent nhét thêm từ phụ "news" vào query dù đã có tham số `topic="news"`. | Thêm quy tắc `<boundaries>` trong prompt chỉ lấy từ khóa chính của chủ đề, bỏ các từ phụ như "news", "today". |
| **R10_missing_handle** | missing_info | `timeline(screenname="sama")` | Agent tự ý đoán bừa tài khoản của Sam Altman là "sama" thay vì hỏi lại. | Bổ sung luật bắt buộc gọi `clarify` (response_type="text") hỏi ý kiến người dùng khi thiếu tham số handle. |
| **R12_confirm_before_send** | wrong_boundary | `send(text="...")` | Agent tự ý đăng tin lên Telegram ngay lập tức không thông báo. | Thiết lập quy định hành động ghi phải qua xác nhận `clarify` (response_type="yes_no") trước khi gọi `send`. |
| **G03_arxiv_search_sort** | wrong_arg_value | `papers(query="\"Prompt Engineering\"")` | LLM tự ý bọc giá trị query trong dấu nháy kép `"..."` gây lệch chuỗi. | Thêm quy tắc cấm bọc giá trị tham số chuỗi trong dấu nháy kép `""` hoặc nháy đơn `''` vào `<boundaries>`. |

---

## B3. Team Eval Cases

Danh sách 10 testcases (5 single-turn và 5 multi-turn) được nhóm tự thiết kế trong file `data/eval_group.json` để kiểm thử độ bền của Agent:

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| **G01_summarize_bullets** | Khả năng định tuyến tóm tắt văn bản dài của người dùng. | `summarizer(text="...", style="bullets")` | **PASS** |
| **G02_export_report** | Khả năng xuất file Markdown vật lý cục bộ. | `exporter(content="...", filename="result.md")` | **PASS** |
| **G03_arxiv_search_sort** | Ánh xạ từ khóa "mới nhất" thành `sort_by="submittedDate"` khi tìm papers. | `papers(query="Prompt Engineering", sort_by="submittedDate")` | **PASS** |
| **G04_missing_url_fetch** | Hỏi tóm tắt "bài này" nhưng thiếu link $\rightarrow$ hỏi lại. | `clarify(response_type="text")` | **PASS** |
| **G05_out_of_scope_cooking** | Yêu cầu nấu phở bò nằm ngoài phạm vi hoạt động của Agent. | Từ chối lịch sự, không gọi bất kỳ tool nào (`no_tool: true`) | **PASS** |
| **G06_multiturn_export_carry** | Đổi hành động từ tóm tắt sang xuất file ở lượt cuối của hội thoại. | `exporter(filename="summarized_report.md")` | **PASS** |
| **G07_multiturn_timeline_limit** | Đổi tài khoản từ Sam Altman sang Elon Musk và giữ nguyên limit ở lượt cuối. | `timeline(screenname="elonmusk", limit=5)` | **PASS** |
| **G08_multiturn_arxiv_limit** | Giảm số lượng bài báo tìm kiếm từ 10 xuống còn 5 ở lượt cuối và giữ sort_by. | `papers(query="LLM Agents", sort_by="submittedDate", max_results=5)` | **PASS** |
| **G09_multiturn_clarify_url** | Hội thoại 3 lượt cung cấp URL thiếu và thực hiện cào nội dung URL. | `fetch(url="https://openai.com/blog/gpt-5")` | **PASS** |
| **G10_multiturn_switch_lookup_social** | Chuyển đổi công cụ tìm kiếm từ Web sang Twitter và giữ nguyên từ khóa GPT-5. | `social_search(query="GPT-5")` | **PASS** |

---

## B4. Live Chat Evidence

Bằng chứng tương tác thực tế ghi nhận từ file transcript hội thoại `transcripts/*.transcript.json`:

1. **Lượt 1 - Yêu cầu tóm tắt:**
   * **User:** *"Tóm tắt đoạn văn bản sau dưới dạng gạch đầu dòng giúp mình: Trí tuệ nhân tạo đang làm thay đổi thế giới. Các mô hình ngôn ngữ lớn ngày càng thông minh hơn."*
   * **Tool Calls:** `summarizer(text="...", style="bullets")`
   * **Outcome:** Agent trả về kết quả tóm tắt gồm 2 gạch đầu dòng rất chi tiết và sạch sẽ.
2. **Lượt 2 - Yêu cầu ghi file:**
   * **User:** *"Lưu nội dung tóm tắt đó ra file 'bao_cao_ai.md' giúp mình."*
   * **Tool Calls:** `exporter(content="...", filename="bao_cao_ai.md")`
   * **Outcome:** Agent xuất file vật lý thành công và phản hồi: *"Successfully exported report to bao_cao_ai.md"*.
3. **Lượt 3 - Thoát:**
   * **User:** `/exit`
   * **Outcome:** Chương trình chat đóng an toàn và xuất file transcript thành công.

---

## B5. Bonus Evidence

Các tính năng điểm thưởng được nhóm hiện thực hóa đầy đủ:

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| **send (Telegram) với xác nhận** | `tools/send/tool.py` + `artifacts/system_prompt.md` | Chỉ thực hiện gửi tin nhắn khi người dùng xác nhận thông qua `clarify` (yes_no) và biến `confirmed=True`. | Tránh việc Agent tự động đăng tải nội dung sai lệch, rác hoặc spam khi chưa được duyệt kiểm duyệt từ con người. |
| **Hai Tool mới nâng cấp** | `tools/summarizer/` + `tools/exporter/` | Phân tích và tóm tắt văn bản thông minh không cần API phụ; Ghi file vật lý trực tiếp lên thư mục đĩa cục bộ. | Các tham số được kiểm soát an toàn để tránh bị lỗi hệ thống tập tin (File System errors). |
| **Streamlit Web UI cao cấp** | `starter_v0/app.py` | Dựng giao diện đẹp mắt, hỗ trợ theo dõi log chạy tool trực quan và tương tác clarification qua nút bấm. | Deployed qua Cloudflare Tunnel rất nhanh và ổn định. |

---

## B6. Reflection

* **Cải tiến thuộc về `system_prompt.md`:** Các chỉ dẫn hành vi (ví dụ: cấm tự ý đoán bừa handle/URL, bắt buộc hỏi ý kiến yes_no trước khi gửi Telegram, từ chối lịch sự các câu hỏi ngoài phạm vi, chỉ trích xuất từ khóa sạch không chứa từ phụ, cấm bọc nháy kép).
* **Cải tiến thuộc về `tools.yaml`:** Việc dịch nghĩa toàn bộ tên mô tả của các Tools và tham số sang tiếng Anh chuẩn giúp cải thiện vượt bậc khả năng khớp nghĩa của LLM, giúp Agent hoạt động chuẩn xác hơn hẳn.
* **Những cải tiến tiếp theo:**
  * Tích hợp thêm cơ sở dữ liệu Vector (Vector Database) cục bộ để hỗ trợ lưu trữ dài hạn (Long-term memory) cho Agent.
  * Tự động đặt lịch (Schedule) để Agent tự cào tin tức và gửi báo cáo định kỳ mỗi buổi sáng lên Telegram channel mà không cần gõ lệnh thủ công.
