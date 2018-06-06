import React from 'react'
import { withRouter } from 'react-router-dom'
import $ from 'jquery'

import Console from './Console'
import UserPanel from './UserPanel'
import Nav from './Nav'
import Content from './Content'
import ItemPanel from './ItemPanel'
import StatusBar from './StatusBar'

import qiniuUpload from './uploader/qiniu'
import conf from './conf'
import api from './api'
import { getTree, Node } from './node'
import { joinPaths, splitBaseName, calcMD5, openTab } from './util'
import { sendMessage } from './serviceworker'

import './css/Explorer.css'

class Explorer extends React.Component {
  state = {
    tree: null,
    uploadPath: null,
    transfer: null,
  }

  componentWillReceiveProps = async (props) => {
    await this.state.tree.setCurrentPath(props.currentPath);
    this.setState({});
  }

  componentDidMount = async () => {
    window.upload = this.openFileSelection;
    const tree = await getTree(this.props.rootPath, this);
    await tree.setCurrentPath(this.props.currentPath);
    this.setState({tree: tree});
  }

  render() {
    const tree = this.state.tree;
    if (!tree) return null;
    return (
      <div className="explorer">
        <header className="horizontal">
          <div className="left child">
            <Console/>
          </div>
          <div className="right child">
            <a
              id="todo"
              href="/?todo"
              target="_blank"
              rel="noopener noreferrer"
            >
              TODO
            </a>
            <UserPanel/>
          </div>
        </header>
        <main className="horizontal">
          <Nav tree={this.state.tree}
            onNodeClicked={this.onNodeClickedInNav}
            onNodeToggled={this.onNodeToggledInNav}
          />
          <Content
            currentDir={this.state.tree.currentDir}
            currentItem={this.state.tree.currentItem}
            onClick={this.onItemClickedInContent}
            onItemDeleted={this.onItemDeleted}
            onItemChange={this.update}
          />
          <ItemPanel node={tree.currentItem || tree.currentDir}/>
        </main>
        <footer>
          <div className="child">
            <StatusBar item={tree.currentItem || tree.currentDir}/>
          </div>
        </footer>
        <div style={{display: 'none'}}>
          <input id="upload"
            type="file"
            multiple
            style={{display: 'none'}}
            onChange={this.onFileInputChange}
          />
        </div>
      </div>
    );
  }

  onNodeClickedInNav = async (node) => {
    if (node.isCurrentDir()) {
      await node.toggle();
    } else {
      this.changeCurrentDir(node);
    }
    this.setState({});
  }

  onItemClickedInContent = async (node) => {
    if (node && node.isCurrentItem()) {
      if (node.meta.listable) {
        this.changeCurrentDir(node);
      } else {
        this.openFile(node);
      }
    } else {
      this.setCurrentItem(node);
    }
    this.update();
  }

  setCurrentItem = (node) => {
    this.state.tree.setCurrentItem(node);
    this.update();
  }

  onItemDeleted = async (node) => {
    const tree = this.state.tree;
    if (node === tree.currentItem) {
      tree.currentItem = null;
    }
    this.update();
  }

  onNodeToggledInNav = () => {
    this.setState({});
  }

  changeCurrentDir = (node) => {
    this.state.tree.setCurrentItem(null);
    this.state.tree.setCurrentDir(node);
    this.props.history.push(node.meta.path);
  }

  openFile = async (node) => {
    if (node.meta.status !== 'done') return;

    await sendMessage({
      op: 'add-download-config',
      meta: node.meta,
      origin: conf.origin,
    });

    //const img = $(`<img src="${node.meta.path}">`);
    //$('body').append(img);

    //fetch(node.meta.path);

    openTab(node.meta.path);
  }

  openFileSelection = (path) => {
    this.setState({
      uploadPath: path || '',
    }, () => $('#upload').click());
  }

  onFileInputChange = async () => {
    let [dirpath, name] = splitBaseName(this.state.uploadPath);
    dirpath = joinPaths(this.getCurrentDirPath(), dirpath);
    const fileInput = $('#upload');
    const files = fileInput[0].files;
    if (files.length === 1) {
      this.doUploadFile(dirpath, name, files[0]);
    } else {
      for (let i = 0; i < files.length; ++i) {
        this.doUploadFile(dirpath, null, files[i]);
      }
    }
    fileInput.val(null);
  }

  getCurrentDirPath = () => {
    return this.state.tree.currentDir.meta.path;
  }

  doUploadFile = async (dirpath, name, file) => {
    name = name || file.name;
    const path = joinPaths(dirpath, name);
    const dir = await this.state.tree.findByPath(dirpath);
    let node = dir.findChildByName(name);
    if (node) {
      //this.setCurrentItem(node);
      //return;
      await node.delete();
    }

    node = makeTransferNode(dir, path, name);
    dir.addFileChild(node);

    const md5 = await calcMD5(file, node.onHashProgress);
    await api.post(path, {
      op: 'touch',
      md5: md5,
      size: file.size,
      mimetype: file.type,
    });
    await dir.update();
    node = await dir.findChildByName(name);
    await node.updateParent();

    const config = {
      path: path,
      dirpath: dirpath,
      name: name,
      md5: md5,
      file: file,
      node: node,
    };

    const contents = node.meta.contents;
    if (contents.some(c => c.type === 'qiniu')) {
      qiniuUpload(config);
    }
  }

  update = () => {
    this.setState({});
  }
}

function makeTransferNode(dir, path, name) {
  const node = new Node({
    path: path,
    name: name,
    listable: false,
  }, dir, dir.tree);
  node.transfer = {
    status: 'hashing',
  };
  return node;
}

Explorer = withRouter(Explorer);

export default Explorer;
