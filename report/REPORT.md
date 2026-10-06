# Báo cáo lab: Tác tử tự tiến hóa và đa tác tử

## 1. Thông tin sinh viên và cấu hình

- Sinh viên: Nguyễn Vũ Quang Anh. Mã sinh viên: `2A202602805`.
- Mô hình: `openai:gpt-4.1-mini`; nhiệt độ: `0`; Deep Agents: `0.7.21`.
- Nền tảng: Windows, backend shell cục bộ và sandbox tạm ngoài kho mã nguồn.
- Thí nghiệm ban đầu: Python `3.13.5`, giới hạn đệ quy `60`; riêng bản ghi cuối `skills-auto/logs-learn` dùng `100` sau một lần chạm giới hạn.
- Đo lại lần này: đúng 6 lượt `skills-auto`, Python `3.11.9` từ `.venv`, giới hạn `100` cho cả sáu; không đổi mô hình, nhiệt độ hoặc nội dung skill.
- Dữ liệu chính: 18 bản ghi trong `results/`. Dữ liệu đo lại lưu riêng tại `experiments/python311-skills-auto/results/`, không ghi đè kết quả ban đầu. Curator được gọi một lần ở vòng trước, không gọi lại lần này. Số bản ghi được giữ không đại diện toàn bộ lịch sử gọi API vì các lần thử/lỗi trước đó không có nhật ký ngân sách đầy đủ.
- Commit giả thuyết: `03e261f`; commit đóng băng: `758263c`; tag: `freeze`. Hạn chế lịch sử đóng băng được nêu tại mục 9.
- Kiểm tra ngoại tuyến sau sửa môi trường: **32 passed**; kiểm tra shell xác nhận Python 3.11, pytest, heredoc, pipeline và không kế thừa biến khóa API.

Các tỉ lệ `6/10`, `5/8` là số check mà **tác tử thực nghiệm** vượt qua, không phải điểm bài lab trên thang 100. Theo `RUBRIC.md`, bài lab còn chấm harness, bằng chứng, phân tích lỗi, skill, quy trình và khả năng tái lập. Kết quả thấp hoặc âm vẫn có giá trị nếu được phân tích đúng.

## 2. Giả thuyết đã ghi trước đánh giá

Giữ nội dung dự đoán của commit `hypotheses`; chỉ dịch sang tiếng Việt, không điều chỉnh giả thuyết theo kết quả mới.

- H1 (subagents so với baseline): Subagents sẽ cải thiện hoặc giữ nguyên điểm trên tác vụ code và dữ liệu phức tạp nhờ giao việc khám phá và triển khai, nhưng cần thêm bước phối hợp và token. Lợi ích dự kiến nhỏ hơn trên tác vụ log ngắn vì chi phí giao việc có thể lớn hơn lợi ích.
- H2 (skills-auto so với baseline): Khi skill được đọc, skills-auto sẽ cải thiện việc tuân thủ quy trình và quy ước tổ chức lặp lại. Hiệu quả có thể không ổn định vì lựa chọn skill phụ thuộc `description`, và skill sinh ra không nhất thiết phù hợp mọi nhóm tác vụ. Việc đọc skill có thể tăng chi phí token.
- H3 (học so với đánh giá): Điểm tác vụ học sẽ cao hơn đánh giá vì tập đánh giá thay đổi dữ liệu và bổ sung quy ước mới. Cải thiện trên tập học nhưng không chuyển sang tập đánh giá sẽ là dấu hiệu quá khớp hoặc skill chưa đủ tổng quát.

Căn cứ thiết kế: `scripts/tour.py` mô tả subagent chỉ nhận lời giao việc; `guides/pseudocode/05_skill_quality.md` giải thích cơ chế nạp dần và vai trò của `description`; `GUIDE.md` nêu khác biệt giữa phản hồi học và quy ước mới ở tập đánh giá. Đây là căn cứ dự đoán, không phải bằng chứng dự đoán đã được xác nhận.

## 3. Làm quen với Deep Agents

1. Tác tử mặc định có công cụ tệp `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, công cụ chạy lệnh `execute` và công cụ giao việc `task`.
2. `task` khởi chạy subagent tạm thời. `general-purpose` có thể tìm kiếm, đọc tệp và thực hiện tác vụ nhiều bước. Mỗi lần gọi mặc định không giữ trạng thái; subagent nhận lời giao việc và trả báo cáo cuối, không tự nhận toàn bộ ngữ cảnh trung gian của tác tử chính.
3. Hai câu trích từ mô tả công cụ trong kết quả `scripts/tour.py`:

   - `task`: “Put full detail in the prompt and state exactly what it should return”. Cần truyền đầy đủ quy tắc, đường dẫn và kết quả cần trả.
   - `execute`: “Quote paths containing spaces”. Đường dẫn có khoảng trắng phải đặt trong dấu nháy.

Mô tả mặc định của `execute` nhắc tới sandbox, nhưng `LocalShellBackend` thực tế chạy bằng quyền tài khoản máy chủ. `virtual_mode=True` và thư mục tạm không tạo cách ly hệ điều hành. Backend chỉ truyền các biến môi trường được chọn, không truyền khóa API cho shell; điều này không ngăn shell đọc tệp máy chủ mà tài khoản có quyền truy cập.

## 4. Phân loại lỗi baseline trên tác vụ học

Chỉ dùng `run.json` và `trace.md` của tác vụ học để phân tích. Các nhóm theo `GUIDE.md`: A bỏ qua đặc tả; B không kiểm chứng; C vá triệu chứng; D bỏ sót dữ liệu/định dạng; E vi phạm quy ước tổ chức; F báo cáo hoàn thành sai; G khác.

| Tác vụ | Check không đạt | Nhóm | Bằng chứng từ phản hồi hoặc trace |
|---|---|---|---|
| code-learn | `tests_not_modified` | G: toàn vẹn bộ test | `detail`: “the original files in tests/ must not be modified”. Check thất bại chưa đủ để khẳng định tác tử sửa mã test; cần phân biệt nguồn với tệp sinh khi chạy. |
| code-learn | `rule_type_hints` | E | Yêu cầu mọi hàm public có annotation cho tất cả tham số và giá trị trả về. |
| code-learn | `rule_regression_tests` | E | Yêu cầu `tests/test_regressions.py`, một test mỗi bug, ít nhất 3 test và chạy đạt. |
| code-learn | `rule_changelog` | E | Yêu cầu ít nhất 3 mục `- fix(<function name>): ...` dưới tiêu đề `## Unreleased`. |
| data-learn | `rule_money_in_cents` | E | Tiền trong `answer.json` phải là số nguyên cent, không phải số USD thập phân. |
| data-learn | `rule_meta_block` | E | Yêu cầu đối tượng `meta` có `source`, `rows_in`, `rows_used`. |
| data-learn | `rule_clean_csv` | E | Yêu cầu `workspace/clean.csv` với thời gian UTC, tên vùng chuẩn và số tiền nguyên cent. |
| logs-learn | `entry_count` | D, kèm thiếu kiểm chứng B | `detail`: “wrong number of entries (got 19)”; trace ghi JSON trực tiếp, không có lệnh chạy parser để đối chiếu toàn bộ đầu vào. |
| logs-learn | `timestamps_utc` | D | `detail`: “7/25 timestamps match”; chuẩn hóa múi giờ chưa đúng trên toàn bộ bản ghi. |
| logs-learn | `exception_fields`, `repeat_counts` | D | Phản hồi lần lượt báo 18 giá trị exception sai và 18 giá trị repeat_count sai. |
| logs-learn | `counts_by_service` | D | `detail`: “counts_by_service: wrong values”; tổng hợp phụ thuộc nhận diện bản ghi và số lần lặp. |
| logs-learn | `rule_service_names`, `rule_sorted_errors`, `rule_schema_header` | E | Yêu cầu tên dịch vụ chữ thường, đổi `-` thành `_`, sắp xếp theo dịch vụ/thời gian, header `schema_version: 2` và `generated_by: log-triage`. |

Baseline học có **15 check không đạt: 9 quy ước và 6 kỹ thuật/toàn vẹn**. Nhóm E chiếm đa số; lỗi kỹ thuật tập trung ở parsing log. Checklist có thể giúp, nhưng chỉ khi được đọc và áp dụng đủ quy tắc.

Bằng chứng phủ định: baseline đạt **12/18 check kỹ thuật** trên tập học. `data-learn` đạt cả 5 check tính toán; `code-learn` đạt 6 check chức năng. Không có căn cứ kết luận mọi tác vụ đều mắc lỗi đọc đặc tả hoặc vá triệu chứng. Các lệnh pytest của baseline code bị lỗi môi trường: đây là hạ tầng, không tính thêm thành lỗi tác tử hay một check thất bại.

## 5. Điều kiện subagents

Ba subagent tùy chỉnh được khai báo:

- `explorer`: đọc tệp/dữ liệu, báo cáo bằng chứng, không sửa tệp.
- `implementer`: thay đổi triển khai, chạy kiểm tra, báo cáo tệp đã sửa.
- `reviewer`: kiểm tra độc lập yêu cầu, hồi quy và trường hợp biên, không sửa triển khai.

Trên tập học, số lần gọi `task` là **0, 1, 1** cho code, data, logs; điểm **6/10, 1/8, 2/9**. Không giao việc ở code là kết quả hợp lệ: tác tử chính trực tiếp sửa hàm và thử chạy test; không thể khẳng định vai trò tùy chỉnh đã được sử dụng ở tác vụ này.

Hai trace học có giao việc thực tế dùng **`subagent_type: general-purpose`**, không phải ba vai trò tùy chỉnh. Đây là khác biệt quan trọng giữa thiết kế và hành vi quan sát được.

Lời giao việc data chứa đường dẫn, định dạng ngày, xử lý trùng/thiếu và năm chỉ số đầu ra. Tuy nhiên, tác tử chính chép các số trả về vào `answer.json` mà không tính lại độc lập trong trace. Với logs, tác tử chính nhận báo cáo mô tả kế hoạch rồi ghi đầu ra rất ngắn mà không xác minh độ bao phủ. Cụm “Acme conventions” không truyền được quy ước ẩn chưa biết. Trace chỉ chứa luồng chính nên không suy diễn chính xác mọi bước nội bộ subagent.

Ở đánh giá, số lời gọi `task` tổng hợp là **0, 3, 1**, điểm **6/11, 5/9, 0/10**. Token trung bình **43.323/lượt**, thấp hơn baseline **69.036/lượt** khoảng **37,2%**. Giao việc không bảo đảm tăng độ chính xác; chi phí thấp hơn không chứng minh hiệu quả hơn khi nhiều check bị bỏ sót.

## 6. Skill do curator tự sinh

Curator dùng phản hồi thất bại và trace của **baseline học**, gọi mô hình một lần và sinh ba skill. Không sửa tay `skills/auto/`, không gọi lại curator lần này.

| Skill | Dòng phần thân | Tính tổng quát, tính đúng và tình huống kích hoạt |
|---|---:|---|
| `enforce-type-annotations` | 7 | Áp dụng rộng cho hàm public, không chép lời giải. Annotation phù hợp phản hồi học. `description` nêu thêm/kiểm tra hàm public, nhưng sửa bug cũng cần quy tắc này. Lệnh mypy phụ thuộc công cụ có sẵn; không nên mặc định đã cài mypy. |
| `maintain-test-integrity` | 9 | Quy trình giữ test gốc và bổ sung regression có thể tái sử dụng. Một test mỗi bug là đúng, nhưng thiếu mức tối thiểu 3 test. Câu cho phép sửa fixture nếu cần có thể mâu thuẫn yêu cầu giữ test gốc. `description` thiên về thêm/sửa test nên có thể bị bỏ qua trong tác vụ chỉ được hiểu là sửa code. |
| `standardize-logging-and-timestamps` | 9 | Tổng quát cho UTC, traceback nhiều dòng, repeated messages, tên dịch vụ và thứ tự đầu ra. `description` phù hợp parsing log. Metadata chỉ nói chung về schema/generator, thiếu hai giá trị cụ thể được phản hồi học yêu cầu. |

Ba skill ngắn và vượt kiểm tra cấu trúc `validate_skill`. Không có skill riêng cho quy ước data hoặc changelog, nên chưa bao phủ toàn bộ lỗi nhóm E. Kiểm tra cấu trúc và marker không chứng minh nội dung đúng hoặc đủ.

Kiểm tra ngoại tuyến bằng mô hình giả xác nhận cả ba tên skill xuất hiện trong system prompt khi bật `use_skills`. Tuy nhiên, cả **6 lượt chính và 6 lượt đo lại đều có `skills_read = 0`**; trace học không có `read_file` đọc `SKILL.md`. Có thể xác nhận metadata được nạp nhưng chưa xác nhận đọc hoặc tuân thủ skill. Không quy lỗi chắc chắn cho `description` hay middleware chỉ từ bộ đếm này.

## 7. Bảng kết quả và lượt đo lại

### 7.1. Thí nghiệm ban đầu

Bảng được dán nguyên từ `report/table.md`, do `lab.compare` tạo từ 18 bản ghi trong `results/`. Giữ nhãn công cụ để đối chiếu: `learning tasks` là tác vụ học; `evaluation tasks` là đánh giá; `Mean tokens per run` là token trung bình mỗi lượt; `Runs that read a skill` là số lượt ghi nhận đọc skill.

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 6/10 | 6/10 | 6/10 |
| data-learn | 5/8 | 1/8 | 5/8 |
| logs-learn | 1/9 | 2/9 | 1/9 |
| code-eval | 6/11 | 6/11 | 6/11 |
| data-eval | 3/9 | 5/9 | 5/9 |
| logs-eval | 1/10 | 0/10 | 6/10 |
| **Mean score - learning tasks** | 0.45 | 0.32 | 0.45 |
| **Mean score - evaluation tasks** | 0.33 | 0.37 | 0.57 |
| **Mean tokens per run** | 69,036 | 43,323 | 84,667 |
| **Runs that read a skill** | 0/6 | 0/6 | 0/6 |

Điểm trung bình là trung bình tỉ lệ `passed/total` từng tác vụ, không gộp số check cả tập. Tất cả bản ghi chính có `skills_modified = false`; `verify_freeze.py` báo `OK` trên lịch sử Git hiện có, với giới hạn diễn giải tại mục 9.

### 7.2. Đo lại 6 lượt skills-auto bằng Python 3.11

Mục tiêu là kiểm tra khả năng cải thiện sau sửa môi trường Windows, không chọn riêng lượt có điểm cao. Cùng bộ skill và mô hình, giới hạn 100 bước. Điểm được lưu tại `experiments/python311-skills-auto/results/`.

| Tác vụ/chỉ số | skills-auto ban đầu | skills-auto đo lại |
|---|---:|---:|
| code-learn | 6/10 | 6/10 |
| data-learn | 5/8 | 5/8 |
| logs-learn | 1/9 | 1/9 |
| code-eval | 6/11 | 6/11 |
| data-eval | 5/9 | 5/9 |
| logs-eval | 6/10 | 1/10 |
| Điểm trung bình tác vụ học | 0,45 | 0,45 |
| Điểm trung bình tác vụ đánh giá | 0,57 | 0,40 |
| Token trung bình mỗi lượt | 84.667 | 66.528 |
| Số lượt ghi nhận đọc skill | 0/6 | 0/6 |

Cả sáu lượt mới không có lỗi runner, giữ hash skill và `skills_modified = false`. Điểm **không tăng**: năm tác vụ giữ nguyên, logs-eval giảm 5 check. Token trung bình giảm khoảng **21,4%**; không kết luận riêng sửa môi trường là nguyên nhân vì giới hạn bước cũng đổi và chỉ có một lượt mỗi tác vụ.

Bằng chứng cải thiện hạ tầng từ trace học mới: agent chạy `PYTHONPATH=workspace pytest ... workspace/tests` và nhận **`6 passed in 0.05s`**. Test code thực sự chạy được; điều này không đồng nghĩa mọi check kỹ thuật/toàn vẹn hoặc quy ước ẩn đều đạt.

## 8. Phân tích kết quả

### 8.1. So sánh điều kiện và giả thuyết

Bộ ban đầu: baseline/skills-auto cùng đạt **0,45** trên học, subagents **0,32**. Đánh giá lần lượt **0,33; 0,37; 0,57**. Skills-auto cao nhất lượt đầu, chủ yếu nhờ logs-eval; đo lại chỉ còn **0,40**, nên lợi thế lớn ban đầu chưa bền vững.

- **H1 chỉ được ủng hộ một phần:** code giữ nguyên; data học giảm, data đánh giá tăng; logs không có lợi ích nhất quán. Dự đoán subagents tốn nhiều token hơn không đúng trong mẫu này.
- **H2 chưa được xác nhận về cơ chế:** không lượt nào ghi nhận đọc skill. Chênh lệch điểm theo điều kiện không chứng minh skill tạo ra cải thiện, nhất là khi check quy ước đánh giá vẫn không đạt.
- **H3 không được ủng hộ đồng đều:** đúng về trung bình baseline, ngược lại ở subagents/skills-auto ban đầu. Riêng skills-auto đo lại, học 0,45 cao hơn đánh giá 0,40. Không quy tất cả chênh lệch cho quá khớp khi độ khó và nhiễu cũng khác nhau.

### 8.2. Check kỹ thuật và quy ước

Thống kê chính từ `scripts/check_breakdown.py`:

| Điều kiện | Kỹ thuật học | Quy ước học | Kỹ thuật đánh giá | Quy ước đánh giá |
|---|---:|---:|---:|---:|
| baseline | 12/18 | 0/9 | 10/18 | 0/12 |
| subagents | 8/18 | 1/9 | 11/18 | 0/12 |
| skills-auto | 12/18 | 0/9 | 17/18 | 0/12 |

Lợi thế skills-auto ban đầu nằm ở kỹ thuật, **không** nằm ở tuân thủ quy ước. Skill thiếu nội dung data/changelog và không có lần đọc được quan sát: đây là hai trở ngại khác nhau, thiếu độ bao phủ và thiếu kích hoạt. Sửa pytest không tự giải quyết hai vấn đề đó.

### 8.3. Kiểm tra skill trước và sau đóng băng

Kết quả Phần 3.4 truy xuất được từ commit `03e261f`. Cùng hash skill:

| Tác vụ | Phần 3.4 | Bản ghi chính sau đóng băng | Đo lại Python 3.11 |
|---|---:|---:|---:|
| code-learn | 3/10 | 6/10 | 6/10 |
| data-learn | 5/8 | 5/8 | 5/8 |
| logs-learn | 1/9 | 1/9 | 1/9 |

Điểm học trung bình từ khoảng **0,35** lên **0,45** dù skill không đổi. Đây là biến động khi chạy lại, không phải bằng chứng curator học thêm. Vòng mới còn đổi runtime/ngân sách bước nên không phải phép lặp thuần túy đo nhiễu. Chưa hoàn thành thử thách lặp đánh giá ít nhất hai lần nữa cho mỗi điều kiện.

### 8.4. Chi phí, quá khớp và rò rỉ

Token trung bình bộ chính: baseline **69.036**, subagents **43.323**, skills-auto **84.667**. Skills-auto tốn hơn baseline khoảng **22,6%** ở vòng đầu; đo lại riêng skills-auto còn **66.528**. Token không đủ để kết luận điều kiện tốt nhất vì còn điểm, độ ổn định và cấu hình.

Phân tích và sửa harness dựa trên tác vụ học và mã hạ tầng. Không mở `tasks/*/check.py`, nội dung `tasks/*-eval/` hoặc trace/JSON đánh giá để rút kinh nghiệm. Điểm đánh giá đọc qua bảng/thống kê tổng hợp. Curator loại vai trò đánh giá, kiểm tra marker trước khi ghi skill: biện pháp hạn chế rò rỉ, không phải chứng minh tuyệt đối không quá khớp. Skill ngắn vẫn có thể thiếu quy tắc hoặc mô tả quá hẹp.

## 9. Hạn chế và tính hợp lệ

1. **Mẫu nhỏ:** ba tác vụ mỗi vai trò; một kết quả log có thể đổi mạnh trung bình.
2. **Ít lần lặp:** một bản ghi mỗi điều kiện/tác vụ ở bộ chính. Đo lại cho thấy logs-eval không ổn định; chưa có khoảng tin cậy đáng tin cậy.
3. **Một mô hình:** chỉ gpt-4.1-mini, nhiệt độ 0; không khái quát sang mô hình khác. Nhiệt độ 0 không bảo đảm mọi lời gọi hoàn toàn giống nhau.
4. **Skill:** cấu trúc hợp lệ nhưng thiếu quy ước data/changelog; `skills_read = 0` khiến quy kết nhân quả rất yếu.
5. **Cấu hình khác nhau:** logs-learn chính có giới hạn 100; bộ mới dùng Python 3.11/Git Bash và giới hạn 100, hai điều kiện kia giữ dữ liệu cũ. Giữ hai bộ riêng, không coi là đối chứng cùng cấu hình.
6. **Sandbox cục bộ:** thư mục tạm/biến môi trường chọn lọc không cách ly hệ điều hành; cần Docker hoặc sandbox thực sự với đầu vào không đáng tin.
7. **Trace:** `render_trace` cắt mỗi nội dung còn tối đa 1.500 ký tự, không lưu chi tiết nội bộ subagent. Không suy ra mô hình chỉ đọc từng đó ký tự hoặc biết chính xác mọi bước con.
8. **Lịch sử đóng băng:** commit `freeze skills` vòng trước được bổ sung sau khi chạy đánh giá và đặt thời gian lùi. `verify_freeze.py = OK` chỉ xác nhận lịch sử Git hiện tại, hash và timestamp đã ghi, không tự chứng minh trình tự thực tế ban đầu. Lần này không chỉnh tag/thời gian commit; sáu lượt mới chạy sau khi bộ skill đã chốt và không sửa skill. Hạn chế quy trình ban đầu cần được công khai, không che bằng kiểm tra tự động.

## 10. Kết luận

Harness vượt **32/32 test ngoại tuyến**. Báo cáo và hai bộ kết quả được giữ đối chiếu; skill đóng băng không bị sửa. Skills-auto có điểm đánh giá **0,57** ở lượt đầu nhưng đo lại chỉ **0,40**, điểm học vẫn **0,45**, không lượt nào ghi nhận đọc skill. Vì vậy **chưa có bằng chứng nâng điểm hoặc cải thiện nhờ skill một cách ổn định**.

Sửa môi trường giúp chạy được test và token trung bình lượt mới thấp hơn. Muốn cải thiện quy ước cần xử lý độ bao phủ và kích hoạt skill. Vòng tiến hóa tiếp theo cần curator sinh skill mới chỉ từ dữ liệu học, lưu thí nghiệm riêng, chốt trước đánh giá và chạy các điều kiện cùng cấu hình. Không sửa bộ skill đã đóng băng hoặc nâng điểm bằng tay.

## Phụ lục: Kiểm tra và tái lập

Chạy ở gốc kho bằng PowerShell. Gọi trực tiếp Python venv tránh nhầm Python hệ thống. `--basetemp` phải là thư mục riêng cho test, không chứa dữ liệu cần giữ vì pytest có thể dọn nội dung của nó.

```powershell
# Không gọi API
.\.venv\Scripts\python.exe -m pytest --basetemp=.pytest-tmp-check
.\.venv\Scripts\python.exe experiments/verify_windows_runtime.py
.\.venv\Scripts\python.exe scripts/verify_freeze.py
.\.venv\Scripts\python.exe scripts/check_breakdown.py
.\.venv\Scripts\python.exe -m lab.compare

# Có gọi API: đúng lệnh dùng cho sáu lượt đo lại
.\.venv\Scripts\python.exe -m lab.runner --condition skills-auto --tasks all --results experiments/python311-skills-auto/results --recursion-limit 100

# Bảng tổng hợp vòng mới, không gọi API
.\.venv\Scripts\python.exe -m lab.compare --results experiments/python311-skills-auto/results

# Kết quả học Phần 3.4 từ lịch sử
git show 03e261f:results/skills-auto/code-learn/run.json
git show 03e261f:results/skills-auto/data-learn/run.json
git show 03e261f:results/skills-auto/logs-learn/run.json
```

Giữ nguyên `tests/`, `tasks/`, `scripts/`, các mô-đun có sẵn, hằng số prompt và `skills/auto/`. Lần này sửa backend trong phần cài đặt sinh viên để dùng Git Bash trên Windows, tìm Python/pytest đúng venv, bổ sung biến Windows cần thiết và ghi phiên bản Python/giới hạn bước vào bản ghi mới. Không tự commit, push hay nộp bài.
