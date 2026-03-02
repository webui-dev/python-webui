# Call Python from JavaScript Example
# pip install --upgrade webui2
from webui import webui

html = """<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <script src="webui.js"></script>
    <title>Call Python from JavaScript Example</title>
    <style>
      body {
        font-family: 'Arial', sans-serif;
        color: white;
        background: linear-gradient(to right, #507d91, #1c596f, #022737);
        text-align: center;
        font-size: 18px;
      }
      button, input {
        padding: 10px;
        margin: 10px;
        border-radius: 3px;
        border: 1px solid #ccc;
        box-shadow: 0 3px 5px rgba(0,0,0,0.1);
        transition: 0.2s;
      }
      button {
        background: #3498db;
        color: #fff;
        cursor: pointer;
        font-size: 16px;
      }
      h1 { text-shadow: -7px 10px 7px rgb(67 57 57 / 76%); }
      button:hover { background: #c9913d; }
      input:focus { outline: none; border-color: #3498db; }
    </style>
  </head>
  <body>
    <h1>WebUI - Call Python from JavaScript</h1>
    <p>Call Python functions with arguments (<em>See the logs in your terminal</em>)</p>
    <button onclick="my_function_string('Hello', 'World');">Call my_function_string()</button>
    <br>
    <button onclick="my_function_integer(123, 456, 789, 12345.6789);">Call my_function_integer()</button>
    <br>
    <button onclick="my_function_boolean(true, false);">Call my_function_boolean()</button>
    <br>
    <button onclick="my_function_raw_binary(new Uint8Array([0x41,0x42,0x43]), big_arr);">
      Call my_function_raw_binary()</button>
    <br>
    <p>Call a Python function that returns a response</p>
    <button onclick="MyJS();">Call my_function_with_response()</button>
    <div>Double: <input type="text" id="MyInputID" value="2"></div>
    <script>
      const arr_size = 512 * 1000;
      const big_arr = new Uint8Array(arr_size);
      big_arr[0] = 0xA1;
      big_arr[arr_size - 1] = 0xA2;
      function MyJS() {
        const MyInput = document.getElementById('MyInputID');
        const number = MyInput.value;
        my_function_with_response(number, 2).then((response) => {
          MyInput.value = response;
        });
      }
    </script>
  </body>
</html>"""


def my_function_string(e: webui.Event):
    # JavaScript: my_function_string('Hello', 'World')
    str_1 = e.get_string()       # index 0
    str_2 = e.get_string_at(1)
    print(f"my_function_string 1: {str_1}")  # Hello
    print(f"my_function_string 2: {str_2}")  # World


def my_function_integer(e: webui.Event):
    # JavaScript: my_function_integer(123, 456, 789, 12345.6789)
    count = e.get_count()
    print(f"my_function_integer: There are {count} arguments in this event")  # 4

    number_1 = e.get_int()          # index 0
    number_2 = e.get_int_at(1)
    number_3 = e.get_int_at(2)
    float_1  = e.get_float_at(3)

    print(f"my_function_integer 1: {number_1}")   # 123
    print(f"my_function_integer 2: {number_2}")   # 456
    print(f"my_function_integer 3: {number_3}")   # 789
    print(f"my_function_integer 4: {float_1}")    # 12345.6789


def my_function_boolean(e: webui.Event):
    # JavaScript: my_function_boolean(true, false)
    status_1 = e.get_bool()       # index 0
    status_2 = e.get_bool_at(1)
    print(f"my_function_boolean 1: {status_1}")   # True
    print(f"my_function_boolean 2: {status_2}")   # False


def my_function_raw_binary(e: webui.Event):
    # JavaScript: my_function_raw_binary(new Uint8Array([0x41,0x42,0x43]), big_arr)
    raw_1 = e.get_bytes()
    raw_2 = e.get_bytes_at(1)
    len_1 = len(raw_1)
    len_2 = len(raw_2)

    hex_1 = " ".join(f"0x{b:02x}" for b in raw_1)
    print(f"my_function_raw_binary 1 ({len_1} bytes): {hex_1}")

    valid = len_2 >= 2 and raw_2[0] == 0xA1 and raw_2[len_2 - 1] == 0xA2
    print(f"my_function_raw_binary 2 big ({len_2} bytes): valid data? {'Yes' if valid else 'No'}")


def my_function_with_response(e: webui.Event):
    # JavaScript: my_function_with_response(number, 2).then(...)
    number = e.get_int()          # index 0
    times  = e.get_int_at(1)
    result = number * times
    print(f"my_function_with_response: {number} * {times} = {result}")
    e.return_int(result)


def main():
    window = webui.Window()

    window.bind("my_function_string",        my_function_string)
    window.bind("my_function_integer",       my_function_integer)
    window.bind("my_function_boolean",       my_function_boolean)
    window.bind("my_function_raw_binary",    my_function_raw_binary)
    window.bind("my_function_with_response", my_function_with_response)

    window.show(html)
    webui.wait()


if __name__ == "__main__":
    main()
